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
import os
import sys

class MainHandler(webapp.RequestHandler):
    def get(self):
      response_body = ['%s: %s' % (key, value)
	 for key, value in sorted(os.environ.items())]
      response_body = '</br>'.join(response_body)
      response_body = response_body + '<br/>The End<br/>'
      response_body = response_body + '</br>'.join(sys.path)
      sys.path.append('C:\\Windows\\system32\\python27.zip', 'C:\\Python27\\DLLs', 'C:\\Python27\\lib', 'C:\\Python27\\lib\\plat-win', 'C:\\Python27\\lib\\lib-tk', 'C:\\Python27', 'C:\\Users\\scherer\\AppData\\Roaming\\Python\\Python27\\site-packages', 'C:\\Python27\\lib\\site-packages', 'C:\\Python27\\lib\\site-packages\\win32', 'C:\\Python27\\lib\\site-packages\\win32\\lib', 'C:\\Python27\\lib\\site-packages\\Pythonwin', 'C:\\Python27\\lib\\site-packages\\setuptools-0.6c11-py2.7.egg-info')

# added
      try:
         import scipy
      except:
         response_body = response_body + "</br>Oops! No scipy"

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
