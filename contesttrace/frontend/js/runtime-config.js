(function () {
    // 线上部署时，把这里替换为你的公网 AI API 地址（不带末尾斜杠）
    // 例如: "https://contesttrace-ai-rerank.onrender.com"
    var PUBLIC_API_BASE = "";

    // 允许通过 localStorage 覆盖，便于临时切换
    // localStorage.setItem("ai_rerank_api", "https://xxx.onrender.com/api/ai/rerank")
    var localApi = (window.localStorage && window.localStorage.getItem("ai_rerank_api")) || "";
    if (localApi) {
        window.AI_RERANK_API = localApi;
        return;
    }

    if (PUBLIC_API_BASE) {
        window.AI_RERANK_API = PUBLIC_API_BASE.replace(/\/$/, "") + "/api/ai/rerank";
        return;
    }

    // GitHub Pages 未配置公网 API 时，保持为空，由业务代码走规则兜底
    window.AI_RERANK_API = "";
})();
