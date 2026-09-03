/**
 * Sveltia CMS 鉴权 Worker（Cloudflare Workers，免费）
 * 作用：代替 GitHub OAuth 的 token 交换（浏览器无法安全持有 client_secret）。
 * 部署：在 Cloudflare 控制台新建 Worker，粘贴本文件；在 Worker 的 Variables 里配置：
 *   GITHUB_CLIENT_ID   —— GitHub OAuth App 的 Client ID
 *   GITHUB_CLIENT_SECRET —— GitHub OAuth App 的 Client Secret
 *   ADMIN_URL          —— 你的后台地址，如 https://www.tuodasheng.com/admin/
 * OAuth App 的 Authorization callback URL 填：https://你的worker.workers.dev/callback
 *
 * 说明：这是最小可用版；生产建议直接部署官方 Worker：
 *   https://github.com/sveltia/sveltia-cms-auth
 */
export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname === "/authorize") {
      const redirectUri = url.origin + "/callback";
      const githubUrl =
        "https://github.com/login/oauth/authorize?client_id=" +
        encodeURIComponent(env.GITHUB_CLIENT_ID) +
        "&redirect_uri=" + encodeURIComponent(redirectUri) +
        "&scope=repo&state=" + crypto.randomUUID();
      return Response.redirect(githubUrl, 302);
    }

    if (url.pathname === "/callback") {
      const code = url.searchParams.get("code");
      const tokenRes = await fetch("https://github.com/login/oauth/access_token", {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify({
          client_id: env.GITHUB_CLIENT_ID,
          client_secret: env.GITHUB_CLIENT_SECRET,
          code,
        }),
      });
      const data = await tokenRes.json();
      const token = data.access_token;
      if (!token) return new Response("GitHub 授权失败", { status: 401 });
      return Response.redirect(env.ADMIN_URL + "?token=" + encodeURIComponent(token), 302);
    }

    return new Response("Not found", { status: 404 });
  },
};
