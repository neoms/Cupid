<template>
  <nav>
    <div class="nav-inner">
      <span class="brand">晓夕成家</span>
      <div class="nav-links">
        <router-link to="/">🏠 首页</router-link>
        <router-link to="/search/natural">🔍 语义搜索</router-link>
        <router-link to="/search/structured">📋 条件筛选</router-link>
        <router-link to="/create">📝 创建资料</router-link>
      </div>
    </div>
  </nav>
  <main>
    <router-view />
  </main>
</template>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background: #f8f9fa; color: #2c3e50; -webkit-font-smoothing: antialiased;
}
nav {
  background: #fff;
  border-bottom: 1px solid #e8ecf0;
  position: sticky; top: 0; z-index: 10;
}
.nav-inner {
  max-width: 1400px; margin: 0 auto;
  display: flex; align-items: center; padding: 0 24px; height: 54px;
}
.brand {
  font-size: 1.1rem; font-weight: 700; color: #e0526e; margin-right: 32px; letter-spacing: 1px;
}
.nav-links { display: flex; gap: 2px; }
.nav-links a {
  padding: 7px 16px; border-radius: 6px; text-decoration: none;
  color: #5a6d80; font-size: 0.9rem; transition: all 0.15s;
}
.nav-links a:hover { background: #f0f2f5; color: #2c3e50; }
.nav-links a.router-link-exact-active { background: #fff0f3; color: #e0526e; font-weight: 600; }
main { min-height: calc(100vh - 54px); }
</style>
