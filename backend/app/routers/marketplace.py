"""API routes for the workflow marketplace."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.routers.auth import get_current_user
from app.services.marketplace.marketplace_service import marketplace_service

router = APIRouter(tags=["marketplace"])


class PublishListingRequest(BaseModel):
    blueprint_id: str
    title: str
    description: str = ""
    category: str = "general"
    tags: list[str] = []
    version: str = "1.0.0"
    org_id: str | None = None


class UpdateListingRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    category: str | None = None
    tags: list[str] | None = None
    version: str | None = None
    status: str | None = None


class RateListingRequest(BaseModel):
    rating: int
    review: str = ""


class ForkListingRequest(BaseModel):
    forked_blueprint_id: str


# === Listings ===


@router.get("/marketplace/listings")
async def list_listings(
    category: str | None = None,
    search: str | None = None,
    sort_by: str = "rating_avg",
    limit: int = 50,
) -> list[dict[str, Any]]:
    """Browse published marketplace listings."""
    return await marketplace_service.list_listings(
        category=category,
        search=search,
        sort_by=sort_by,
        limit=limit,
    )


@router.get("/marketplace/listings/{listing_id}")
async def get_listing(listing_id: str) -> dict[str, Any]:
    """Get a marketplace listing."""
    listing = await marketplace_service.get_listing(listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing


@router.get("/marketplace/my-listings")
async def my_listings(
    user: Any = Depends(get_current_user),  # noqa: B008
) -> list[dict[str, Any]]:
    """Get current user's listings."""
    return await marketplace_service.get_user_listings(user.id)


@router.post("/marketplace/listings", status_code=201)
async def publish_listing(
    body: PublishListingRequest,
    user: Any = Depends(get_current_user),  # noqa: B008
) -> dict[str, Any]:
    """Publish a blueprint to the marketplace."""
    return await marketplace_service.publish_listing(
        user_id=user.id,
        blueprint_id=body.blueprint_id,
        title=body.title,
        description=body.description,
        category=body.category,
        tags=body.tags,
        version=body.version,
        org_id=body.org_id,
    )


@router.put("/marketplace/listings/{listing_id}")
async def update_listing(
    listing_id: str,
    body: UpdateListingRequest,
    user: Any = Depends(get_current_user),  # noqa: B008
) -> dict[str, Any]:
    """Update a listing."""
    updates = body.model_dump(exclude_none=True)
    result = await marketplace_service.update_listing(listing_id, user.id, updates)
    if not result:
        raise HTTPException(status_code=404, detail="Listing not found or not owner")
    return result


@router.delete("/marketplace/listings/{listing_id}", status_code=204)
async def delete_listing(
    listing_id: str,
    user: Any = Depends(get_current_user),  # noqa: B008
):
    """Delete a listing."""
    deleted = await marketplace_service.delete_listing(listing_id, user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Listing not found or not owner")


# === Ratings ===


@router.post("/marketplace/listings/{listing_id}/rate")
async def rate_listing(
    listing_id: str,
    body: RateListingRequest,
    user: Any = Depends(get_current_user),  # noqa: B008
) -> dict[str, Any]:
    """Rate a marketplace listing."""
    if body.rating < 1 or body.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be 1-5")
    return await marketplace_service.rate_listing(
        listing_id=listing_id,
        user_id=user.id,
        rating=body.rating,
        review=body.review,
    )


@router.get("/marketplace/listings/{listing_id}/ratings")
async def get_ratings(listing_id: str) -> list[dict[str, Any]]:
    """Get all ratings for a listing."""
    return await marketplace_service.get_ratings(listing_id)


# === Forks ===


@router.post("/marketplace/listings/{listing_id}/fork", status_code=201)
async def fork_listing(
    listing_id: str,
    body: ForkListingRequest,
    user: Any = Depends(get_current_user),  # noqa: B008
) -> dict[str, Any]:
    """Fork a marketplace listing."""
    return await marketplace_service.fork_listing(
        listing_id=listing_id,
        user_id=user.id,
        forked_blueprint_id=body.forked_blueprint_id,
    )


@router.get("/marketplace/listings/{listing_id}/forks")
async def get_forks(listing_id: str) -> list[dict[str, Any]]:
    """Get all forks of a listing."""
    return await marketplace_service.get_forks(listing_id)
