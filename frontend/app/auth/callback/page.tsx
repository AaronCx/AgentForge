"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { supabase } from "@/lib/supabase";

export default function AuthCallbackPage() {
  const router = useRouter();

  useEffect(() => {
    // Supabase puts tokens in the URL hash after OAuth redirect.
    // We need to let Supabase client parse them, set the cookie, then redirect.
    async function handleCallback() {
      const { data, error } = await supabase.auth.getSession();

      if (error || !data.session) {
        // If no session yet, wait a moment for Supabase to process the hash
        await new Promise((r) => setTimeout(r, 500));
        const retry = await supabase.auth.getSession();
        if (retry.data.session) {
          document.cookie = `sb-access-token=${retry.data.session.access_token}; path=/; max-age=${60 * 60}; SameSite=Lax`;
          router.push("/dashboard");
          return;
        }
        // Still no session — redirect to login
        router.push("/login");
        return;
      }

      document.cookie = `sb-access-token=${data.session.access_token}; path=/; max-age=${60 * 60}; SameSite=Lax`;
      router.push("/dashboard");
    }

    handleCallback();
  }, [router]);

  return (
    <div className="flex min-h-screen items-center justify-center">
      <p className="text-muted-foreground">Signing you in...</p>
    </div>
  );
}
