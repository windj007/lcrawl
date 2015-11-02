{
	"PREPROCESSORS" : [
	                   { "constructor" : "lcrawl.preprocessors.html.HtmlParser" }
	                   ],
    "PAGE_ANALYZERS" : [
                        { "constructor" : "lcrawl.page_analyzers.base.ContentTypeExtractor" },
                        { "constructor" : "lcrawl.page_analyzers.base.RawContentAssigner" },
                        { "constructor" : "lcrawl.page_analyzers.html.HtmlTextExtractor" }
                        ],
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
	"DOWNLOAD_DELAY" : 1,
	"CONCURRENT_REQUESTS_PER_DOMAIN" : 3,
	"COOKIES_ENABLED" : true,
	"TELNETCONSOLE_ENABLED" : false,
	"AUTOTHROTTLE_ENABLED" : true,
	"AUTOTHROTTLE_START_DELAY" : 5,
	"AUTOTHROTTLE_MAX_DELAY" : 60,
	"AUTOTHROTTLE_DEBUG" : false,
	"DEFAULT_REQUEST_HEADERS" : {
		"Accept-Language" : "ru"
	}
}