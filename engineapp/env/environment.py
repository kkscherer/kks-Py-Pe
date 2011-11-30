# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
import os 

class MainHandler(webapp.RequestHandler):
    def get(self):
      response_body = ['%s: %s' % (key, value)
	 for key, value in sorted(os.environ.items())]
      response_body = '</br>'.join(response_body)
      response_body = response_body + '<br/>The End<br/>'
# added

#      self.response.status = 205
      self.response.headers['Content-Type'] = 'text/html'
      self.response.headers['Content-Length'] = str(len(response_body))

      self.response.out.write(response_body)

# added end

def main():
    application = webapp.WSGIApplication([('/.*', MainHandler)],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
