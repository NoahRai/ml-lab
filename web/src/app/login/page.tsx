"use client";

import { useState } from "react";

import { createSupabaseBrowserClient } from "@/lib/supabase/client";

export default function LoginPage() {
  const [message, setMessage] = useState("");
  async function signIn() {
    const supabase = createSupabaseBrowserClient();
    if (!supabase) return setMessage("Configure Supabase environment variables to enable sign-in.");
    const { error } = await supabase.auth.signInWithOAuth({ provider: "google", options: { redirectTo: `${window.location.origin}/auth/callback` } });
    if (error) setMessage(error.message);
  }
  return <main className="grid min-h-screen place-items-center bg-[#fafaf9] p-6 text-[#161614]"><section className="w-full max-w-md rounded-2xl border border-[#e3e2dc] bg-white p-8"><p className="text-xs font-semibold tracking-[0.15em] text-[#697b68]">ML LAB</p><h1 className="mt-3 text-3xl font-semibold tracking-tight">Save your experiments</h1><p className="mt-3 text-sm leading-6 text-[#706f68]">Sign in to keep experiment history private to your account.</p><button className="mt-7 w-full rounded-lg bg-[#161614] px-4 py-3 text-sm font-medium text-white" onClick={signIn} type="button">Continue with Google</button>{message && <p className="mt-4 text-sm text-[#9b3a2e]">{message}</p>}</section></main>;
}
