// Simple dev proxy to forward /api requests to the Flask backend on port 8001
const http = require('http');
const httpProxy = require('http-proxy');

const proxy = httpProxy.createProxyServer({});

const server = http.createServer(function(req, res) {
  if (req.url.startsWith('/api/')) {
    // Rewrite /api/... -> /...
  req.url = req.url.replace(/^\/api/, '');
  proxy.web(req, res, { target: 'http://localhost:8002' });
  } else {
    res.writeHead(404);
    res.end('Not proxied');
  }
});

const port = process.env.PORT || 3001;
server.listen(port, () => console.log(`Dev proxy listening on http://localhost:${port}`));
