import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'standalone',
  // Allow the app to be accessed from any host (important for Cloud Run)
  images: {
    unoptimized: true,
  },
};

export default nextConfig;
