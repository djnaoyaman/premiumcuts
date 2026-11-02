"""Pure source/host contract. No browser, HTTP, native share or clipboard calls."""
from pathlib import Path
import ast,unittest
from preview_network_policy import YOUTUBE_FAMILY_HOSTS,youtube_family_request

ROOT=Path(__file__).resolve().parents[1]
class PreviewPolicy(unittest.TestCase):
 def test_block_each_host_and_subdomains(self):
  for host in YOUTUBE_FAMILY_HOSTS:
   for url in [f'https://{host}/asset',f'https://sub.{host}/image.jpg',f'https://{host.upper()}./embed',f'http://{host}:80/a',f'//{host}/b']:
    with self.subTest(url=url):self.assertTrue(youtube_family_request(url))
 def test_thumbnails_media_embed_api_avatar(self):
  for url in ['https://i.ytimg.com/vi/example/hqdefault.jpg','https://www.youtube-nocookie.com/embed/example','https://rr1---sn-test.googlevideo.com/videoplayback','https://youtubei.googleapis.com/youtubei/v1/player','https://yt3.ggpht.com/a','https://yt3.googleusercontent.com/a']:
   with self.subTest(url=url):self.assertTrue(youtube_family_request(url))
 def test_preserve_local_fonts_and_other_existing_resources(self):
  for url in ['http://127.0.0.1:8000/premiumcuts/','https://fonts.googleapis.com/css2?family=DM+Sans','https://fonts.gstatic.com/s/a.woff2','https://djnaoyaman.github.io/premiumcuts/style.css','data:image/svg+xml,a','https://notyoutube.com/a','https://youtube.com.example.test/a']:
   with self.subTest(url=url):self.assertFalse(youtube_family_request(url))
 def test_malformed_host_fails_closed(self):self.assertTrue(youtube_family_request('https://[invalid'))
 def test_actual_renderer_first_operation_aborts_blocked_host(self):
  source=(ROOT/'scripts/render_social_cards.py').read_text();tree=ast.parse(source)
  handler=next(n for n in ast.walk(tree) if isinstance(n,ast.AsyncFunctionDef) and n.name=='static_assets')
  guard=handler.body[0];self.assertIsInstance(guard,ast.If)
  self.assertEqual(ast.unparse(guard.test),'youtube_family_request(route.request.url)')
  self.assertEqual([ast.unparse(x) for x in guard.body],['await route.abort()','return'])
  self.assertIn("route.request.resource_type in {'script', 'media', 'websocket'}",source)
  self.assertIn("await context.route('**/*', static_assets)",source)
  # Later route.fetch is only registered for the two font hosts, not a provider.
  font_routes=[ast.literal_eval(n.args[0]) for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='route' and len(n.args)>1 and isinstance(n.args[1],ast.Name) and n.args[1].id=='font_route']
  self.assertEqual(set(font_routes),{'https://fonts.googleapis.com/**','https://fonts.gstatic.com/**'})
 def test_full_renderer_and_image_gate_remain(self):
  workflow=(ROOT/'.github/workflows/pages.yml').read_text()
  self.assertIn('run: python scripts/render_social_cards.py\n',workflow)
  self.assertIn("if: github.event_name != 'pull_request' || !github.event.pull_request.draft",workflow)
  self.assertIn("python scripts/verify_metadata.py ${{ github.event_name == 'pull_request' && github.event.pull_request.draft && '--structure-only' || '' }}",workflow)
  self.assertLess(workflow.index('python scripts/verify_preview_network_policy.py'),workflow.index('python scripts/render_social_cards.py'))

if __name__=='__main__':unittest.main(verbosity=2)
