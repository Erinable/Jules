/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,

  // 环境变量
  env: {
    NEXT_PUBLIC_API_URL:
      process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
    NEXT_PUBLIC_WS_URL: process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000",
  },

  // 输出配置（用于生产部署）
  output: "standalone",

  // 图片配置
  images: {
    domains: ["localhost"],
  },

  // 禁用 X-Powered-By 头（安全性）
  poweredByHeader: false,

  // 压缩配置
  compress: true,

  // 开发环境配置
  ...(process.env.NODE_ENV === "development" && {
    // 热重载
    webpack: (config, { dev, isServer }) => {
      if (dev && !isServer) {
        config.watchOptions = {
          poll: 1000,
          aggregateTimeout: 300,
        };
      }
      return config;
    },
  }),
};

module.exports = nextConfig;
