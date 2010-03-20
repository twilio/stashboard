/*
Copyright (c) 2007-2008 the OTHER media Limited
Licensed under the BSD license, http://ojay.othermedia.org/license.html
*/
// @require ojay/core-min
/**
 * @overview
 * <p><tt>Ojay.HTTP</tt> wraps the <tt>YAHOO.util.Connect</tt> module to provide a more succinct
 * API for making Ajax requests. It's called <tt>HTTP</tt> to emphasise what's actually going on
 * in an Ajax call: we're just making an HTTP request. <tt>Ojay.HTTP</tt> makes you use HTTP verbs
 * as methods, to make it clear what's going on to anyone reading the code. A quick example:</p>
 *
 * <pre><code>    Ojay.HTTP.GET('/index.html', {ajaxLayout: true}, {
 *         onSuccess: function(response) {
 *             alert(response.responseText);
 *         }
 *     });</code></pre>
 *
 * <p>This illustrates the basic pattern of making an HTTP request. Start with the verb (<tt>GET</tt>,
 * <tt>POST</tt>, <tt>PUT</tt>, <tt>DELETE</tt> or <tt>HEAD</tt>), then pass in the URL and the
 * parameters you want to send to the server. These parameters will be turned into a query string
 * or a POST message, depending on the verb used. The URL may contain a query string, but its
 * parameters will be overridden by the parameters object:</p>
 *
 * <pre><code>    // Request is: GET /index.html?id=900&ajaxLayout=true
 *     Ojay.HTTP.GET('/index.html?id=45&ajaxLayout=true', {id: 900})</code></pre>
 *
 * <p>You can define callbacks called <tt>onSuccess</tt> (fired on any reponse with a 2xx status
 * code), <tt>onFailure</tt> (fired on any 3xx, 4xx or 5xx response) or status-code-specific
 * callbacks, like <tt>on404</tt>:</p>
 *
 * <pre><code>    Ojay.HTTP.POST('/posts/create', {title: '...'}, {
 *         onSuccess: function(response) {
 *             alert('Post created!');
 *         },
 *         on403: function(response) {
 *             alert('Permission denied!);
 *         }
 *     });</code></pre>
 *
 * <p>The <tt>response</tt> object passed to your callbacks will be an instance of <tt>HTTP.Response</tt>,
 * which wraps the response object returned by YUI. It has convenience methods for manipulating
 * the response and inserting it into the document. Its methods are listed below. You can use the
 * <tt>response</tt> methods to chain after HTTP calls for more sentence-like code:</p>
 *
 * <pre><code>    Ojay.HTTP.GET('/index.html').insertInto('#container').evalScriptTags();</pre></code>
 *
 * <p>It's best to use this chaining for really simple stuff -- just remember the chain is called
 * asynchronously after the HTTP request completes, so any code following a chain like this should
 * not assume that the content has been inserted into the document or that the scripts have been
 * run.</p>
 *
 * <pre><ocde>    Ojay.HTTP.GET('/index.html').insertInto('#container');  // asynchronous insertion
 *     var text = Ojay('#container').node.innerHTML;
 *             // text does NOT contain the HTTP response yet!</code></pre>
 *
 * <p>For anything beyond really simple stuff, it's best to use explicit callback functions.</p>
 *
 * <p><tt>HTTP.Response</tt> methods are available in chains following calls to <tt>on()</tt>,
 * <tt>animate()</tt> and <tt>wait()</tt> on <tt>DomCollection</tt> objects. e.g.:</p>
 *
 * <pre><code>    Ojay('input[type=submit]').on('click')
 *             ._(Ojay.HTTP.POST, '/posts/update/34', ...)
 *             .insertInto('#message');</pre></code>
 *
 * <p>You can even pass functions into the parameters object, and <tt>HTTP</tt> will execute them
 * at the time the request is made:</p>
 *
 * <pre><code>    Ojay('#link').on('click')
 *             ._(Ojay.HTTP.POST, '/images/save_width', {width: Ojay('#foo').method('getWidth')});</code></pre>
 *
 * <p><tt>Ojay('#foo').method('getWidth')</tt> is a function bound to <tt>Ojay('#foo')</tt>; when
 * the POST request is made, it will be executed and the return value will be sent to the server
 * in the <tt>width</tt> parameter.</p>
 */
Ojay.HTTP = new JS.Singleton(/** @scope Ojay.HTTP */{
    include: Ojay.Observable,
    
    /**
     * <p>Object containing named references to XmlHttpRequest ready states.</p>
     */
    READY_STATE: {
        UNINITIALIZED:  0,
        LOADING:        1,
        LOADED:         2,
        INTERACTIVE:    3,
        COMPLETE:       4
    },
    
    /**
     * <p>List of verbs supported by <tt>Ojay.HTTP</tt>.</p>
     */
    VERBS: 'GET POST PUT DELETE HEAD'.split(/\s+/)
});

Ojay.HTTP.VERBS.forEach(function(verb) {
    Ojay.HTTP[verb] = function(url, parameters, callbacks) {
        var request = new Ojay.HTTP.Request(verb, url, parameters, callbacks);
        request._begin();
        return request.chain;
    };
});

/**
 * <p>The <tt>HTTP.Request</tt> class is used to instantiate Ajax calls to the server. This
 * is for internal consumption -- use <tt>HTTP.GET</tt> et al to make requests.</p>
 * @constructor
 * @class HTTP.Request
 */
Ojay.HTTP.Request = new JS.Class(/** @scope Ojay.HTTP.Request.prototype */{
    
    /**
     * @param {String} verb         One of 'GET', 'POST', 'PUT', 'DELETE', or 'HEAD'
     * @param {String} url          The URL to request
     * @param {Object} parameters   Key-value pairs to be used as a query string or POST message
     * @param {Object} callbacks    Object containing callback functions
     */
    initialize: function(verb, url, parameters, callbacks) {
        this.verb           = verb.toUpperCase();
        if (Ojay.HTTP.VERBS.indexOf(this.verb) == -1) return;
        this._url           = url;
        this._parameters    = parameters || {};
        this._callbacks     = callbacks || {};
        this.chain          = new JS.MethodChain();
    },
    
    /**
     * <p>Returns the URI of the request.
     */
    getURI: function() {
        if (this.uri) return this.uri;
        return this.uri = Ojay.URI.build(this._url, this._parameters);
    },
    
    /**
     * <p>Makes the HTTP request and sets up all the callbacks.</p>
     */
    _begin: function() {
        var uri         = this.getURI();
        var url         = (this.verb == 'POST') ? uri._getPathWithHost() : uri.toString();
        var postData    = (this.verb == 'POST') ? uri.getQueryString() : undefined;
        Ojay.HTTP.notifyObservers('request', {receiver: this});
        
        YAHOO.util.Connect.asyncRequest(this.verb, url, {
            scope: this,
            
            // Will fire onSuccess, on2xx, and the chain
            success: function(transport) {
                var response = new Ojay.HTTP.Response(this, transport);
                var success  = this._callbacks.onSuccess;
                var onStatus = this._callbacks['on' + response.status];
                var complete = this._callbacks.onComplete;
                success  && Function.from(success)(response);
                onStatus && Function.from(onStatus)(response);
                complete && Function.from(complete)(response);
                this.chain.fire(response);
                Ojay.HTTP.notifyObservers('success', {receiver: response});
                Ojay.HTTP.notifyObservers(response.status, {receiver: response});
                Ojay.HTTP.notifyObservers('complete', {receiver: response});
            },
            
            // Will fire onFailure, on3xx, on4xx, on5xx
            failure: function(transport) {
                var response = new Ojay.HTTP.Response(this, transport);
                var failure  = this._callbacks.onFailure;
                var onStatus = this._callbacks['on' + response.status];
                var complete = this._callbacks.onComplete;
                failure  && Function.from(failure)(response);
                onStatus && Function.from(onStatus)(response);
                complete && Function.from(complete)(response);
                Ojay.HTTP.notifyObservers('failure', {receiver: response});
                Ojay.HTTP.notifyObservers(response.status, {receiver: response});
                Ojay.HTTP.notifyObservers('complete', {receiver: response});
            }
            
        }, postData);
    }
});

/**
 * <p>The <tt>HTTP.Response</tt> class is used to wrap XmlHttpRequest transport objects in Ajax
 * callback functions. The argument passed into your Ajax callbacks, and used as the base of chains
 * after <tt>GET</tt>/<tt>POST</tt>/etc calls, will be an object of this class. It contains fields
 * copied straight from the transport object, including <tt>status</tt>, <tt>statusText</tt>,
 * <tt>responseText</tt>, and <tt>responseXML</tt>.</p>
 * class.
 * @constructor
 * @class HTTP.Response
 */
Ojay.HTTP.Response = new JS.Class(/** @scope Ojay.HTTP.Response.prototype */{
    
    /**
     * @param {HTTP.Request} request an HTTP.Request object
     * @param {Object} transport An XmlHttpRequest transport object
     */
    initialize: function(request, transport) {
        'status statusText responseText responseXML readyState'.split(/\s+/).forEach(function(key) {
            this[key] = transport[key];
        }, this);
        this.request = request;
        this.transport = transport;
    },
    
    /**
     * <p>Inserts the response's body text into the given <tt>elements</tt> at the given
     * <tt>position</tt> (default is <tt>'replace'</tt>). See <tt>DomCollection#insert.</tt>.
     * If no position is specified, will accept any object with a <tt>setContent()</tt> method.</p>
     * @param {String|HTMLElement|DomCollection} elements
     * @param {String} position
     * @returns {HTTP.Response}
     */
    insertInto: function(elements, position) {
        elements = elements.setContent ? elements : Ojay(elements);
        var content = (this.responseText || '').stripScripts();
        if (!position) elements.setContent(content);
        else elements.insert(content, position);
        return this;
    },
    
    /**
     * @returns {HTTP.Response}
     */
    evalScripts: function() {
        if (this.responseText) this.responseText.evalScripts();
        return this;
    },
    
    /**
     * <p>Returns the result of parsing the response body as JSON.</p>
     * @returns {Object|Array}
     */
    parseJSON: function() {
        return (this.responseText || '').parseJSON();
    },
    
    /**
     * @returns {HTTP.Response}
     */
    evalScriptTags: function() {
        return this.evalScripts();
    }.traced('evalScriptTags() is deprecated. Use evalScripts() instead.', 'warn')
});

(function() {
    
    var HTTP = Ojay.HTTP;
    
    // Precompiled regexps
    var PATTERNS = {
        JS:     /\.js$/i,
        CSS:    /\.css$/i
    };
    
    var IFRAME_NAME = '__ojay_cross_domain__';
    
    var createIframe = function() {
        Ojay(document.body).insert('<iframe name="' + IFRAME_NAME + '" style="display: none;"></iframe>', 'top');
    }.runs(1);
    
    var determineAssetType = function(url) {
        switch (true) {
            case PATTERNS.JS.test(url) :    return 'script';    break;
            case PATTERNS.CSS.test(url) :   return 'css';       break;
            default :                       return 'script';    break;
        }
    };
    
    JS.extend(HTTP, /** @scope Ojay.HTTP */{
        
        /**
         * <p><tt>Ojay.HTTP.GET</tt> is overloaded to provide support for <tt>YAHOO.util.Get</tt>,
         * which allows loading of new script/css assets into the document, even from other domains.
         * If you try to <tt>GET</tt> a URL from another domain, Ojay automatically uses the <tt>Get</tt>
         * utility to load the asset into the document. For example, to talk to a JSON web service on
         * another domain:</p>
         *
         * <pre><code>    Ojay.HTTP.GET('http://example.com/posts/45.json', {
         *         user: 'your_username',
         *         api_key: '4567rthdtyue566w34',
         *         callback: 'handleJSON'
         *     });
         *     
         *     var handleJSON = function(json) {
         *         // process json object
         *     };</code></pre>
         *
         * <p>If you request a URL on your own domain, Ojay will always make an Ajax request rather
         * than a Get-utility request. If you want to load assets from your own domain or talk to
         * your own web service, use <tt>Ojay.HTTP.load()</tt>.</p>
         *
         * @param {String} url          The URL to request
         * @param {Object} parameters   Key-value pairs to be used as a query string
         * @param {Object} callbacks    Object containing callback functions
         * @returns {MethodChain}
         */
        GET: HTTP.GET.wrap(function(ajax, url, parameters, callbacks) {
            if (Ojay.URI.parse(url).isLocal() || !YAHOO.util.Get) return ajax(url, parameters, callbacks);
            this.load(url, parameters, callbacks);
        }),
        
        /**
         * <p><tt>Ojay.HTTP.POST</tt> is overloaded to allow POST requests to other domains using
         * hidden forms and iframes. Using the same syntax as for Ajax requests to your own domain,
         * you can send data to any URL to like. An example:</p>
         *
         * <pre><code>    Ojay.HTTP.POST('http://example.com/posts/create', {
         *         user: 'your_username',
         *         api_key: '4567rthdtyue566w34',
         *         title: 'A new blog post',
         *         content: 'Lorem ipsum dolor sit amet...'
         *     });</code></pre>
         *
         * <p>Due to same-origin policy restrictions, you cannot access the response for cross-
         * domain POST requests, so no callbacks may be used.</p>
         *
         * @param {String} url          The URL to request
         * @param {Object} parameters   Key-value pairs to be used as a POST message
         * @param {Object} callbacks    Object containing callback functions
         * @returns {MethodChain}
         */
        POST: HTTP.POST.wrap(function(ajax, url, parameters, callbacks) {
            if (Ojay.URI.parse(url).isLocal()) return ajax(url, parameters, callbacks);
            this.send(url, parameters);
        }),
        
        /**
         * <p>Uses the YUI Get utility to load assets into the current document. Pass in the URL you
         * want to load, parameters for the query string, and callback functions if you need them.</p>
         *
         * <p>Ojay automatically infers which type of asset (script or stylesheet) you want to load
         * from the URL. If it ends in '.css', Ojay makes a stylesheet request, otherwise it loads
         * a script file.</p>
         *
         * @param {String} url          The URL to request
         * @param {Object} parameters   Key-value pairs to be used as a query string
         * @param {Object} callbacks    Object containing callback functions
         */
        load: function(url, parameters, callbacks) {
            var path = Ojay.URI.parse(url).path,
                assetType = determineAssetType(path);
            
            YAHOO.util.Get[assetType](Ojay.URI.build(url, parameters).toString(), callbacks || {});
        },
        
        /**
         * <p>Allows cross-domain POST requests by abstracting away the details required to implement
         * such a technique. An invisible form and iframe are injected into the document to send
         * the data you specify to the required URL. There is no way of communicating across frames
         * from different domains, so you cannot use any callbacks to see what happened to your data.</p>
         *
         * @param {String} url          The URL to send data to
         * @param {Object} parameters   Key-value pairs to be used as a POST message
         */
        send: function(url, parameters) {
            var form = this._buildPostForm(url, parameters, true);
            createIframe();
            Ojay(document.body).insert(form.node, 'top');
            form.node.submit();
            form.remove();
        },
        
        _buildPostForm: function(url, parameters, postToIframe) {
            var uri = Ojay.URI.build(url, parameters),
                postUrl = uri._getPathWithHost(),
                params = uri.params;
            
            var attributes = {action: postUrl, method: 'POST'};
            if (postToIframe) attributes.target = IFRAME_NAME;
            
            return Ojay( Ojay.HTML.form(attributes, function(HTML) {
                for (var field in params)
                    HTML.input({ type: 'hidden', name: field, value: String(params[field]) });
            }) ).hide();
        }
    });
    
    HTTP.GET.redirectTo = function(url, parameters) {
        window.location.href = Ojay.URI.build(url, parameters).toString();
    };
    
    HTTP.POST.redirectTo = function(url, parameters) {
        var form = HTTP._buildPostForm(url, parameters, false).node;
        Ojay(document.body).insert(form, 'top');
        form.submit();
    };
    
    JS.MethodChain.addMethods(HTTP);
})();

/**
 * @constructor
 * @class URI
 */
Ojay.URI = new JS.Class({
    extend: {
        /**
         * @param {String} string
         * @returns {String}
         */
        sanitize: function(string) {
            return String(string).trim().replace('&amp;', '&').replace('&#38;', '&');
        },
        
        /**
         * @param {String} string
         * @returns {URI}
         */
        parse: function(string) {
            if (string instanceof this) return string;
            var uri = new this;
            
            string = this.sanitize(string)
                .replace(/^(\w+)(:\/+)/,    function(match, capture, keep) { uri.protocol = capture; return keep; })
                .replace(/^:\/+([^\:\/]+)/, function(match, capture) { uri.domain = capture;    return ''; })
                .replace(/^:(\d+)/,         function(match, capture) { uri.port = capture;      return ''; })
                .replace(/^[^\?\#]+/,       function(match, capture) { uri.path = match;        return ''; })
                .replace(/#(.*)$/,          function(match, capture) { uri.hash = capture;      return ''; });
            
            if (!uri.port) uri.port = (uri.domain == this.local.domain)
                    ? this.local.port
                    : this.DEFAULT_PORTS[uri.protocol];
            
            if (uri.path.charAt(0) != '/' && uri.domain == this.local.domain)
                uri.path = this.local.directory + uri.path;
            
            if (/^\?/.test(string)) string.slice(1).split('&').forEach(function(pair) {
                var bits = pair.split('=');
                uri.setParam(bits[0], bits[1]);
            });
            return uri;
        },
        
        /**
         * @param {String} url
         * @param {Object} params
         * @returns {URI}
         */
        build: function(url, params) {
            var uri = this.parse(url), params = params || {}, value;
            for (var key in params) {
                value = (typeof params[key] == 'function') ? params[key]() : params[key];
                uri.setParam(key, value);
            }
            return uri;
        },
        
        /**
         * @param {String|URI} a
         * @param {String|URI} b
         * @returns {Boolean}
         */
        compare: function(a,b) {
            return this.parse(a).equals(b);
        },
        
        DEFAULT_PORTS: {
            http:       '80',
            https:      '443'
        }
    },
    
    /**
     */
    initialize: function() {
        this.protocol = this.klass.local.protocol;
        this.domain   = this.klass.local.domain;
        this.path     = '';
        this.keys     = [];
        this.params   = {};
        this.toString = this._toString;
    },
    
    /**
     * @returns {String}
     */
    _toString: function() {
        var string = this._getPathWithHost(), params = [];
        var queryString = this.getQueryString();
        if (queryString.length) string += '?' + queryString;
        if (this.hash) string += '#' + this.hash;
        return string;
    },
    
    _getPathWithHost: function() {
        return this._getProtocolString() + (this.domain||'') + this._getPortString() + (this.path||'');
    },
    
    /**
     * @returns {String}
     */
    getQueryString: function() {
        return this.keys.sort().map(function(key) {
            return encodeURIComponent(key) + '=' + encodeURIComponent(this.params[key]);
        }, this).join('&');
    },
    
    /**
     * @returns {String}
     */
    _getProtocolString: function() {
        return this.protocol ? this.protocol + '://' : '';
    },
    
    /**
     * @returns {String}
     */
    _getPortString: function() {
        if (!this.port || this.port == this.klass.DEFAULT_PORTS[this.protocol]) return '';
        return ':' + this.port;
    },
    
    /**
     * @param {String|URI} uri
     * @returns {Boolean}
     */
    equals: function(uri) {
        uri = this.klass.parse(uri);
        if (this.domain != uri.domain || this.protocol != uri.protocol || this.port != uri.port ||
                this.path != uri.path || this.hash != uri.hash) return false;
        if (!this.paramsEqual(uri)) return false;
        return true;
    },
    
    /**
     * @param {String} key
     * @param {String} value
     */
    setParam: function(key, value) {
        var bits = [key, value].map(decodeURIComponent).map('trim');
        if (this.keys.indexOf(bits[0]) == -1) this.keys.push(bits[0]);
        this.params[bits[0]] = bits[1];
    },
    
    /**
     * @param {String|URI} uri
     * @returns {Boolean}
     */
    paramsEqual: function(uri) {
        uri = this.klass.parse(uri);
        for (var key in this.params) { if (this.params[key] != uri.params[key]) return false; }
        for (key in uri.params) { if (this.params[key] != uri.params[key]) return false; }
        return true;
    },
    
    /**
     * @returns {Boolean}
     */
    isLocal: function() {
        return  this.protocol == this.klass.local.protocol &&
                this.domain == this.klass.local.domain &&
                this.port == this.klass.local.port;
    }
});

Ojay.URI.extend({
    local: {
        protocol:   window.location.protocol.replace(/\W/g, ''),
        domain:     window.location.hostname,
        directory:  window.location.pathname.replace(/[^\/]*$/, '')
    }
});

Ojay.URI.local.port = window.location.port || Ojay.URI.DEFAULT_PORTS[Ojay.URI.local.protocol || 'http'];

JS.extend(String.prototype, {
    parseURI:   Ojay.URI.method('parse').methodize(),
    equalsURI:  Ojay.URI.method('compare').methodize()
});
