from django.shortcuts import render


def license(request, name=None):
    return render(request, "../templates/info.html", context={
        "info": True,
        "index":True,
        "title": "Legal",
        "subtitle": "Legal information regarding the StatsForTor project",
        "text": """
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, 
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, 
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
<br>
StatsForTor is produced independently from the Tor® anonymity software and carries no guarantee from The Tor Project about quality, suitability or anything else.
<br>
StatsForTor uses data from the Onionoo API, all data accuracy depends on the API responses. StatsForTor does not guarantee any data accuracy of precision.
""".replace("\n","")
    })
