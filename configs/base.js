{
	"PREPROCESSORS" : [
	                   { "constructor" : "lcrawl.preprocessors.web.HtmlParser" }
    ],
    "PAGE_ANALYZERS" : [],
	"TRANSITION_EXTRACTORS" : [
	                           {
	                        	   "constructor" : "lcrawl.transition.html.PluggableHtmlLinkTransitionExtractor",
	                        	   "kwargs" : {
	                        		   "TRANSITION_PROCESSORS" : [
	                        		                              { "constructor" : "lcrawl.transition.base.NormalizeUrls" },
	                        		                              { "constructor" : "lcrawl.transition.html.LinkLabelTokens" }
	                        		                              ]
	                        	   }
	                           }
	                           ],
	"USER_AGENT" : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36",
	"CONCURRENT_REQUESTS" : 16,
	"DOWNLOAD_DELAY" : 3,
	"CONCURRENT_REQUESTS_PER_DOMAIN" : 2
	"COOKIES_ENABLED" : true,
	"TELNETCONSOLE_ENABLED" : false,
	"AUTOTHROTTLE_ENABLED" : true,
	"AUTOTHROTTLE_START_DELAY" : 5,
	"AUTOTHROTTLE_MAX_DELAY" : 60,
	"AUTOTHROTTLE_DEBUG" : false
}