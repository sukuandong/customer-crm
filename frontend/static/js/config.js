/* 统一基础地址：
   - 通过本地文件双击打开（file://）时，请求发往本机 FastAPI 服务；
   - 通过服务访问（http://）时，走同源相对路径。 */
(function () {
  window.APP_BASE = location.protocol === 'file:' ? 'http://127.0.0.1:8000' : '';
})();
