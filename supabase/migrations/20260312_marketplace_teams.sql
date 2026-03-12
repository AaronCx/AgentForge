-- v1.7.0: Workflow Marketplace + Team Features
-- Marketplace listings, ratings, forks
-- Organizations, members, RBAC

-- ========================================
-- Organizations
-- ========================================
CREATE TABLE IF NOT EXISTS organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    description TEXT DEFAULT '',
    owner_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    avatar_url TEXT DEFAULT '',
    settings JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_organizations_owner ON organizations(owner_id);
CREATE UNIQUE INDEX idx_organizations_slug ON organizations(slug);

ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Org members can read their orgs"
    ON organizations FOR SELECT
    USING (
        auth.uid() = owner_id
        OR auth.uid() IN (SELECT user_id FROM org_members WHERE org_id = id)
    );

CREATE POLICY "Org owners can manage"
    ON organizations FOR ALL
    USING (auth.uid() = owner_id);

-- ========================================
-- Organization Members
-- ========================================
CREATE TABLE IF NOT EXISTS org_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    role TEXT NOT NULL DEFAULT 'member',
    -- role: owner, admin, member, viewer
    invited_by UUID REFERENCES auth.users(id),
    joined_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(org_id, user_id)
);

CREATE INDEX idx_org_members_org ON org_members(org_id);
CREATE INDEX idx_org_members_user ON org_members(user_id);

ALTER TABLE org_members ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Members can read own org memberships"
    ON org_members FOR SELECT
    USING (
        auth.uid() = user_id
        OR org_id IN (SELECT id FROM organizations WHERE owner_id = auth.uid())
    );

CREATE POLICY "Admins can manage members"
    ON org_members FOR ALL
    USING (
        org_id IN (SELECT id FROM organizations WHERE owner_id = auth.uid())
        OR (org_id IN (SELECT org_id FROM org_members WHERE user_id = auth.uid() AND role IN ('admin', 'owner')))
    );

-- ========================================
-- Marketplace Listings
-- ========================================
CREATE TABLE IF NOT EXISTS marketplace_listings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    blueprint_id UUID NOT NULL REFERENCES blueprints(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    org_id UUID REFERENCES organizations(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    description TEXT DEFAULT '',
    category TEXT DEFAULT 'general',
    tags TEXT[] DEFAULT '{}',
    version TEXT DEFAULT '1.0.0',
    status TEXT NOT NULL DEFAULT 'published',
    -- status: draft, published, unlisted, archived
    fork_count INTEGER DEFAULT 0,
    rating_avg REAL DEFAULT 0,
    rating_count INTEGER DEFAULT 0,
    install_count INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}'::jsonb,
    published_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_marketplace_user ON marketplace_listings(user_id);
CREATE INDEX idx_marketplace_status ON marketplace_listings(status);
CREATE INDEX idx_marketplace_category ON marketplace_listings(category);
CREATE INDEX idx_marketplace_rating ON marketplace_listings(rating_avg DESC);

ALTER TABLE marketplace_listings ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Published listings are public"
    ON marketplace_listings FOR SELECT
    USING (status = 'published' OR auth.uid() = user_id);

CREATE POLICY "Users can manage own listings"
    ON marketplace_listings FOR ALL
    USING (auth.uid() = user_id);

-- ========================================
-- Marketplace Ratings
-- ========================================
CREATE TABLE IF NOT EXISTS marketplace_ratings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    listing_id UUID NOT NULL REFERENCES marketplace_listings(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    review TEXT DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(listing_id, user_id)
);

CREATE INDEX idx_ratings_listing ON marketplace_ratings(listing_id);

ALTER TABLE marketplace_ratings ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Ratings are public"
    ON marketplace_ratings FOR SELECT
    USING (true);

CREATE POLICY "Users can manage own ratings"
    ON marketplace_ratings FOR ALL
    USING (auth.uid() = user_id);

-- ========================================
-- Marketplace Forks
-- ========================================
CREATE TABLE IF NOT EXISTS marketplace_forks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    listing_id UUID NOT NULL REFERENCES marketplace_listings(id) ON DELETE CASCADE,
    source_blueprint_id UUID NOT NULL REFERENCES blueprints(id) ON DELETE CASCADE,
    forked_blueprint_id UUID NOT NULL REFERENCES blueprints(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_forks_listing ON marketplace_forks(listing_id);
CREATE INDEX idx_forks_user ON marketplace_forks(user_id);

ALTER TABLE marketplace_forks ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can see own forks"
    ON marketplace_forks FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can create forks"
    ON marketplace_forks FOR INSERT
    WITH CHECK (auth.uid() = user_id);
