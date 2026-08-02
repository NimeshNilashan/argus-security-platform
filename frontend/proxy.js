// frontend/middleware.js
import { clerkMiddleware } from "@clerk/nextjs/server";
import { NextResponse } from "next/server";

export default clerkMiddleware(async (auth, req) => {
    const { userId } = auth();
    const { pathname } = req.nextUrl;

    // If user is signed in and on home page → go to dashboard
    if (userId && pathname === '/') {
        console.log('✅ Redirecting / → /dashboard');
        return NextResponse.redirect(new URL('/dashboard', req.url));
    }

    // Allow /dashboard to load - let the component handle auth
    return NextResponse.next();
});

export const config = {
    matcher: ['/', '/dashboard', '/dashboard/:path*'],
};