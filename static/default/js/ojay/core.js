/*
Copyright (c) 2007-2008 the OTHER media Limited
Licensed under the BSD license, http://ojay.othermedia.org/license.html
*/
// @require yui
// @require ojay/js-class-min
/**
 * <p>Returns an object that wraps a collection of DOM element references by parsing
 * the given query using a CSS selector engine.</p>
 *
 * <p>Aliased as <tt>$()</tt>.</p>
 *
 * @params {String|Array} query
 * @returns {DomCollection}
 */
var Ojay = function() {
    var elements = [], arg, i, n;
    for (i = 0, n = arguments.length; i < n; i++) {
        arg = arguments[i];
        if (typeof arg == 'string') arg = Ojay.query(arg);
        if (arg.toArray) arg = arg.toArray();
        if (!(arg instanceof Array)) arg = [arg];
        elements = elements.concat(arg);
    }
    return new Ojay.DomCollection(elements.unique());
};

(function(Dom) {
    JS.extend(Ojay, /** @scope Ojay */{
        
        query: function(selector, node) {
            return document.querySelectorAll
                    ? Array.from((node || document).querySelectorAll(selector))
                    : YAHOO.util.Selector.query(selector, node);
        },
        
        /**
         * <p>Returns an Ojay Collection containing zero or one element that matches the ID. Used
         * for situations where IDs contains dots, slashes, etc.</p>
         * @param {String} id
         * @returns {DomCollection}
         */
        byId: function(id) {
            var element = document.getElementById(id);
            return new this.DomCollection(element ? [element] : []);
        },
        
        /**
         * <p>Changes the alias of the <tt>Ojay()</tt> function to the given <tt>alias</tt>.
         * If the alias is already the name of an existing function, that function will be
         * stored and overridden. The next call to <tt>changeAlias</tt> or <tt>surrenderAlias</tt>
         * will restore the original function.</p>
         * @param {String} alias
         */
        changeAlias: function(alias) {
            this.surrenderAlias();
            this.ALIAS = String(alias);
            this.__alias = (typeof window[this.ALIAS] == 'undefined') ? null : window[this.ALIAS];
            window[this.ALIAS] = this;
        },
        
        /**
         * <p>Gives control of the shorthand function back to whichever script implemented
         * it before Ojay. After using this function, use the <tt>Ojay()</tt> function
         * instead of the shorthand.</p>
         * @returns {Boolean}
         */
        surrenderAlias: function() {
            if (this.__alias === null) {
                if (this.ALIAS) delete window[this.ALIAS];
                return false;
            }
            window[this.ALIAS] = this.__alias;
            return true;
        },
        
        /**
         * <p>Tells Ojay to trace calls to the methods you name. Only accepts methods on
         * <tt>Ojay.DomCollection.prototype</tt>.</p>
         * @param {String}
         */
        log: function() {
            Array.from(arguments).forEach(function(method) {
                this[method] = this[method].traced(method + '()');
            }, Ojay.DomCollection.prototype);
        },
        
        /**
         * <p>Returns an object with width and height properties specifying the size of the
         * document.</p>
         * @returns {Object}
         */
        getDocumentSize: function() {
            return {
                width: Dom.getDocumentWidth(),
                height: Dom.getDocumentHeight()
            };
        },
        
        /**
         * <p>Returns an object with left and top properties specifying the scroll offsets
         * document.</p>
         * @returns {Object}
         */
        getScrollOffsets: function() {
            return {
                left: Dom.getDocumentScrollLeft(),
                top: Dom.getDocumentScrollTop()
            };
        },
        
        /**
         * <p>Returns an object with width and height properties specifying the size of the
         * viewport.</p>
         * @returns {Object}
         */
        getViewportSize: function() {
            return {
                width: Dom.getViewportWidth(),
                height: Dom.getViewportHeight()
            };
        },
        
        /**
         * <p>Returns a <tt>Region</tt> object representing the currently visible area of
         * the document within the browser viewport.</p>
         * @returns {Region}
         */
        getVisibleRegion: function() {
            var viewport = this.getViewportSize(), scrolls = this.getScrollOffsets();
            return new this.Region({
                top:    scrolls.top,    bottom: scrolls.top + viewport.height,
                left:   scrolls.left,   right:  scrolls.left + viewport.width
            });
        }
    });
})(YAHOO.util.Dom);

Ojay.changeAlias('$');

/**
 * <p>This object contains definitions for <tt>Array</tt> instance methods defined
 * by Mozilla in JavaScript versions 1.6 and 1.8. They are applied to the <tt>Array</tt>
 * prototype as required to bring all browsers up to scratch.</p>
 *
 * <p>Definitions are taken from <a
 * href="http://developer.mozilla.org/en/docs/Core_JavaScript_1.5_Reference:Global_Objects:Array#Methods">Mozilla's
 * implementations</a> (made available under the MIT license).</p>
 */
Ojay.ARRAY_METHODS = {
    
    /**
     * <p>Returns the first index at which a given element can be found in the array, or
     * <tt>-1</tt> if it is not present.</p>
     */
    indexOf: function(elt /*, from*/) {
        var len = this.length;
        
        var from = Number(arguments[1]) || 0;
        from = (from < 0) ? Math.ceil(from) : Math.floor(from);
        if (from < 0) from += len;
        
        for (; from < len; from++) {
            if (from in this && this[from] === elt)
                return from;
        }
        return -1;
    },
    
    /**
     * <p>Returns the last index at which a given element can be found in the array, or
     * <tt>-1</tt> if it is not present. The array is searched backwards,
     * starting at <tt>fromIndex</tt>.</p>
     */
    lastIndexOf: function(elt /*, from*/) {
        var len = this.length;
        
        var from = Number(arguments[1]);
        if (isNaN(from)) {
            from = len - 1;
        }
        else {
          from = (from < 0) ? Math.ceil(from) : Math.floor(from);
          if (from < 0)
                from += len;
          else if (from >= len)
                from = len - 1;
        }
        
        for (; from > -1; from--) {
            if (from in this && this[from] === elt)
                return from;
        }
        return -1;
    },
    
    /**
     * <p><tt>filter</tt> calls a provided callback function once for each element in an
     * array, and constructs a new array of all the values for which <tt>callback</tt>
     * returns a <tt>true</tt> value. <tt>callback</tt> is invoked only for indexes of
     * the array which have assigned values; it is not invoked for indexes which have been
     * deleted or which have never been assigned values. Array elements which do not pass
     * the callback test are simply skipped, and are not included in the new array.</p>
     *
     * <p><tt>callback</tt> is invoked with three arguments: the value of the element, the
     * index of the element, and the <tt>Array</tt> object being traversed.</p>
     *
     * <p>If a <tt>thisObject</tt> parameter is provided to <tt>filter</tt>, it will be
     * used as the <tt>this</tt> for each invocation of the callback. If it is not provided,
     * or is <tt>null</tt>, the global object associated with callback is used instead.</p>
     *
     * <p><tt>filter</tt> does not mutate the array on which it is called.</p>
     *
     * <p>The range of elements processed by filter is set before the first invocation of
     * <tt>callback</tt>. Elements which are appended to the array after the call to
     * <tt>filter</tt> begins will not be visited by <tt>callback</tt>. If existing elements
     * of the array are changed, or deleted, their value as passed to <tt>callback</tt> will
     * be the value at the time <tt>filter</tt> visits them; elements that are deleted are
     * not visited.</p>
     */
    filter: function(fun /*, thisp*/) {
        var len = this.length;
        if (typeof fun != "function")
            throw new TypeError();
        
        var res = new Array();
        var thisp = arguments[1];
        for (var i = 0; i < len; i++) {
            if (i in this) {
                var val = this[i]; // in case fun mutates this
                if (fun.call(thisp, val, i, this))
                    res.push(val);
            }
        }
        
        return res;
    },
    
    /**
     * <p><tt>forEach</tt> executes the provided function (<tt>callback</tt>) once for each
     * element present in the array. <tt>callback</tt> is invoked only for indexes of the
     * array which have assigned values; it is not invoked for indexes which have been
     * deleted or which have never been assigned values.</p>
     *
     * <p><tt>callback</tt> is invoked with three arguments: the value of the element, the
     * index of the element, and the <tt>Array</tt> object being traversed.</p>
     *
     * <p>If a <tt>thisObject</tt> parameter is provided to <tt>forEach</tt>, it will be used
     * as the <tt>this</tt> for each invocation of the callback. If it is not provided, or is
     * <tt>null</tt>, the global object associated with <tt>callback</tt> is used instead.</p>
     *
     * <p><tt>forEach</tt> does not mutate the array on which it is called.</p>
     *
     * <p>The range of elements processed by <tt>forEach</tt> is set before the first
     * invocation of <tt>callback</tt>. Elements which are appended to the array after the call
     * to <tt>forEach</tt> begins will not be visited by <tt>callback</tt>. If existing elements
     * of the array are changed, or deleted, their value as passed to <tt>callback</tt> will be
     * the value at the time <tt>forEach</tt> visits them; elements that are deleted are not
     * visited.</p>
     */
    forEach: function(fun /*, thisp*/) {
        var len = this.length;
        if (typeof fun != "function")
            throw new TypeError();
        
        var thisp = arguments[1];
        for (var i = 0; i < len; i++) {
            if (i in this)
                fun.call(thisp, this[i], i, this);
        }
    },
    
    /**
     * <p><tt>every</tt> executes the provided callback function once for each element
     * present in the array until it finds one where <tt>callback</tt> returns a
     * <tt>false</tt> value. If such an element is found, the <tt>every</tt> method
     * immediately returns <tt>false</tt>. Otherwise, if <tt>callback</tt> returned a
     * <tt>true</tt> value for all elements, <tt>every</tt> will return <tt>true</tt>.
     * <tt>callback</tt> is invoked only for indexes of the array which have assigned
     * values; it is not invoked for indexes which have been deleted or which have never
     * been assigned values.</p>
     *
     * <p><tt>callback</tt> is invoked with three arguments: the value of the element,
     * the index of the element, and the <tt>Array</tt> object being traversed.</p>
     *
     * <p>If a <tt>thisObject</tt> parameter is provided to <tt>every</tt>, it will be
     * used as the <tt>this</tt> for each invocation of the callback. If it is not
     * provided, or is <tt>null</tt>, the global object associated with <tt>callback</tt>
     * is used instead.</p>
     *
     * <p><tt>every</tt> does not mutate the array on which it is called.</p>
     *
     * <p>The range of elements processed by <tt>every</tt> is set before the first
     * invocation of <tt>callback</tt>. Elements which are appended to the array after
     * the call to <tt>every</tt> begins will not be visited by <tt>callback</tt>. If
     * existing elements of the array are changed, their value as passed to <tt>callback</tt>
     * will be the value at the time <tt>every</tt> visits them; elements that are deleted
     * are not visited. <tt>every</tt> acts like the "for all" quantifier in mathematics.
     * In particular, for an empty array, it returns <tt>true</tt>. (It is vacuously true
     * that all elements of the empty set satisfy any given condition.)</p>
     */
    every: function(fun /*, thisp*/) {
        var len = this.length;
        if (typeof fun != "function")
            throw new TypeError();
        
        var thisp = arguments[1];
        for (var i = 0; i < len; i++) {
            if (i in this && !fun.call(thisp, this[i], i, this))
                return false;
        }
        
        return true;
    },
    
    /**
     * <p><tt>map</tt> calls a provided callback function once for each element in an array,
     * in order, and constructs a new array from the results. <tt>callback</tt> is invoked
     * only for indexes of the array which have assigned values; it is not invoked for
     * indexes which have been deleted or which have never been assigned values.</p>
     *
     * <p><tt>callback</tt> is invoked with three arguments: the value of the element, the
     * index of the element, and the <tt>Array</tt> object being traversed.</p>
     *
     * <p>If a <tt>thisObject</tt> parameter is provided to <tt>map</tt>, it will be used as
     * the <tt>this</tt> for each invocation of the callback. If it is not provided, or is
     * <tt>null</tt>, the global object associated with <tt>callback</tt> is used instead.</p>
     *
     * <p><tt>map</tt> does not mutate the array on which it is called.</p>
     *
     * <p>The range of elements processed by <tt>map</tt> is set before the first invocation
     * of <tt>callback</tt>. Elements which are appended to the array after the call to
     * <tt>map</tt> begins will not be visited by <tt>callback</tt>. If existing elements of
     * the array are changed, or deleted, their value as passed to <tt>callback</tt> will be
     * the value at the time <tt>map</tt> visits them; elements that are deleted are not
     * visited.</p>
     */
    map: function(fun /*, thisp*/) {
        var len = this.length;
        if (typeof fun != "function")
            throw new TypeError();
        
        var res = new Array(len);
        var thisp = arguments[1];
        for (var i = 0; i < len; i++) {
            if (i in this)
                res[i] = fun.call(thisp, this[i], i, this);
        }
        
        return res;
    },
    
    /**
     * <p><tt>some</tt> executes the callback function once for each element present in the
     * array until it finds one where <tt>callback</tt> returns a <tt>true</tt> value. If such
     * an element is found, <tt>some</tt> immediately returns <tt>true</tt>. Otherwise,
     * <tt>some</tt> returns <tt>false</tt>. <tt>callback</tt> is invoked only for indexes of
     * the array which have assigned values; it is not invoked for indexes which have been
     * deleted or which have never been assigned values.</p>
     *
     * <p><tt>callback</tt> is invoked with three arguments: the value of the element, the
     * index of the element, and the <tt>Array</tt> object being traversed.</p>
     *
     * <p>If a <tt>thisObject</tt> parameter is provided to <tt>some</tt>, it will be used as
     * the <tt>this</tt> for each invocation of the callback. If it is not provided, or is
     * <tt>null</tt>, the global object associated with <tt>callback</tt> is used instead.</p>
     *
     * <p><tt>some</tt> does not mutate the array on which it is called.</p>
     *
     * <p>The range of elements processed by <tt>some</tt> is set before the first invocation
     * of <tt>callback</tt>. Elements that are appended to the array after the call to
     * <tt>some</tt> begins will not be visited by <tt>callback</tt>. If an existing, unvisited
     * element of the array is changed by <tt>callback</tt>, its value passed to the visiting
     * callback will be the value at the time that <tt>some</tt> visits that element's index;
     * elements that are deleted are not visited.</p>
     */
    some: function(fun /*, thisp*/) {
        var len = this.length;
        if (typeof fun != "function")
            throw new TypeError();
        
        var thisp = arguments[1];
        for (var i = 0; i < len; i++) {
            if (i in this && fun.call(thisp, this[i], i, this))
                return true;
        }
        
        return false;
    },
    
    /**
     * <p>Apply a function simultaneously against two values of the array (from
     * left-to-right) as to reduce it to a single value.</p>
     *
     * <p><tt>reduce</tt> executes the callback function once for each element present in the
     * array, excluding holes in the array, receiving four arguments: the initial value (or
     * value from the previous callback call), the value of the current element, the current
     * index, and the array over which iteration is occurring.</p>
     */
    reduce: function(fun /*, initial*/) {
        var len = this.length;
        if (typeof fun != "function")
            throw new TypeError();
        
        // no value to return if no initial value and an empty array
        if (len == 0 && arguments.length == 1)
            throw new TypeError();
        
        var i = 0;
        if (arguments.length >= 2) {
            var rv = arguments[1];
        }
        else {
            do {
                if (i in this) {
                    rv = this[i++];
                    break;
                }
                
                // if array contains no values, no initial value to return
                if (++i >= len)
                    throw new TypeError();
            } while (true);
        }
        
        for (; i < len; i++) {
            if (i in this)
                rv = fun.call(null, rv, this[i], i, this);
        }
        
        return rv;
    },
    
    /**
     * <p>Apply a function simultaneously against two values of the array (from
     * right-to-left) as to reduce it to a single value.</p>
     *
     * <p><tt>reduceRight</tt> executes the callback function once for each element present in
     * the array, excluding holes in the array, receiving four arguments: the initial value (or
     * value from the previous callback call), the value of the current element, the current
     * index, and the array over which iteration is occurring.</p>
     */
    reduceRight: function(fun /*, initial*/) {
        var len = this.length;
        if (typeof fun != "function")
            throw new TypeError();
        
        // no value to return if no initial value, empty array
        if (len == 0 && arguments.length == 1)
            throw new TypeError();
        
        var i = len - 1;
        if (arguments.length >= 2) {
            var rv = arguments[1];
        }
        else {
            do {
                if (i in this) {
                    rv = this[i--];
                    break;
                }
                
                // if array contains no values, no initial value to return
                if (--i < 0)
                    throw new TypeError();
            } while (true);
        }
        
        for (; i >= 0; i--) {
            if (i in this)
                rv = fun.call(null, rv, this[i], i, this);
        }
        
        return rv;
    },
    
    /**
     * <p>Returns a new array containing all the elements of the original array but with
     * any duplicate entries removed.</p>
     * @returns {Array}
     */
    unique: function() {
        var results = [], i, n, arg;
        for (i = 0, n = this.length; i < n; i++) {
            arg = this[i];
            if (results.indexOf(arg) == -1)
                results.push(arg);
        }
        return results;
    },
    
    /**
     * <p>A shorthand for <tt>array.filter(func).length</tt>.</p>
     */
    count: function(fun, thisp) {
        return this.filter(fun, thisp).length;
    }
};

JS.extend(Array.prototype, Ojay.ARRAY_METHODS);

/**
 * Functional extensions: Copyright (c) 2005-2008 Sam Stephenson / the Prototype team,
 * released under an MIT-style license.
 */
JS.extend(Function.prototype, /** @scope Function.prototype */{
    
    /**
     * <p>'Masks' the internals of a function by setting its toString and valueOf methods
     * to return the masking function instead of the receiver. This can be used to make sure,
     * for example, that functions like JS.Class's callSuper() that rely on stringifying
     * functions for intrspection still work as desired.</p>
     * @param {Function} wrapper
     * @returns {Function}
     */
    _mask: function(wrapper) {
        this.valueOf = function() { return wrapper; };
        this.toString = function() { return wrapper.toString(); };
        return this;
    },
    
    /**
     * <p>Returns a new function that does the same thing as the original function, but has
     * some of its arguments preset. A contrived example:</p>
     *
     * <pre><code>    var add = function(a, b) { return a + b; };
     *     add(3, 5)  // --> 8
     *     
     *     var add12 = add.partial(12);  // 'a' is preset to 12
     *     add12(7)  // --> 19</code></pre>
     *
     * <p>More information <a href="http://prototypejs.org/api/function/curry">in the
     * Prototype documentation</a>. (Prototype calls this method <tt>curry</tt>, though
     * that's not strictly what it does.)</p>
     *
     * @returns {Function}
     */
    partial: function() {
        if (!arguments.length) return this;
        var method = this, args = Array.from(arguments);
        return function() {
            return method.apply(this, args.concat(Array.from(arguments)));
        }._mask(this);
    },
    
    /**
     * <p>Returns a copy of the function that is self-currying, i.e. every time you call it, it
     * returns a curried version of itself until it's got all its required arguments.</p>
     *
     * <pre><code>    var adder = function(a,b,c) {
     *         return a + b + c;
     *     };
     *     
     *     var add = adder.curry();
     *     
     *     add(1)(2)(3)  // --> 6
     *     add(7,8)(23)  // --> 38</code></pre>
     *
     * @param {Number} n
     * @returns {Function}
     */
    curry: function(n) {
        var method = this, n = n || this.length;
        return function() {
            if (arguments.length >= n) return method.apply(this, arguments);
            return method.partial.apply(arguments.callee, arguments);
        }._mask(this);
    },
    
    /**
     * <p>Allows you to 'intercept' calls to existing functions and manipulate their input and
     * output, providing aspect-oriented programming functionality. More information and
     * examples <a href="http://prototypejs.org/api/function/wrap">in the Prototype docs</a>.</p>
     * @param {Function} wrapper
     * @returns {Function}
     */
    wrap: function(wrapper) {
        var method = this;
        return function() {
            return wrapper.apply(this, [method.bind(this)].concat(Array.from(arguments))); 
        }._mask(this);
    },
    
    /**
     * <p>Returns a version of the function that, rather taking some argument <tt>foo</tt> as
     * its first argument, can be applied as a method of <tt>foo</tt>.</p>
     *
     * <pre><code>    var hexToDec = function(string) {
     *         var number = ... // convert hex string to decimal
     *         return number;
     *     };
     *     
     *     hexToDec('ff')   // --> 255
     *     
     *     String.prototype.hexToDec = hexToDec.methodize();
     *     'ff'.hexToDec()  // --> 255</code></pre>
     *
     * @returns {Function}
     */
    methodize: function() {
        if (this._methodized) return this._methodized;
        var method = this;
        return this._methodized = function() {
            return method.apply(null, [this].concat(Array.from(arguments)));
        }._mask(this);
    },
    
    /**
     * <p>Effectively does the opposite of <tt>methodize</tt>: it converts a function from a
     * method that uses <tt>this</tt> to refer to its operand, into one that takes the operand
     * as its first argument. This is useful for building iterators, amongst other things.</p>
     *
     * <pre><code>    var upper = "".toUpperCase.functionize();
     *     var strings = ['foo', 'bar', 'baz', ... ];
     *     
     *     var caps = strings.map(upper);
     *     // --> ['FOO', 'BAR', 'BAZ', ... ]</code></pre>
     *
     * @returns {Function}
     */
    functionize: function() {
        if (this._functionized) return this._functionized;
        var method = this;
        return this._functionized = function() {
            var args = Array.from(arguments);
            return method.apply(args.shift(), args);
        }._mask(this);
    },
    
    /**
     * <p>Returns a function that returns the result of applying the function to its arguments,
     * but that logs its input and output to the Firebug console. Derived from a similar function
     * in Oliver Steele's Functional library.</p>
     *
     * Copyright: Copyright 2007 by Oliver Steele.  All rights reserved.
     * http://osteele.com/sources/javascript/functional/
     *
     * @param {String} name
     * @param {String} func
     * @returns {Function}
     */
    traced: function(name, func) {
        var method = this, name = name || this, func = func || 'info';
        return function() {
            window.console && console[func](name, ' called on ', this, ' with ', arguments);
            var result = method.apply(this, arguments);
            window.console && console[func](name, ' -> ', result);
            return result;
        }._mask(this);
    },
    
    /**
     * <p>Returns a copy of the function that will only run the specified number of times. Note
     * that if the function is an instance method, it will run the given number of times in total,
     * not per instance.</p>
     * @param {Number} times
     * @returns {Function}
     */
    runs: function(times) {
        var method = this, count = 0;
        return function() {
            return (count++ < times) ? method.apply(this, arguments) : undefined;
        }._mask(this);
    }
});

/**
 * String extensions: Copyright (c) 2005-2008 Sam Stephenson / the Prototype team,
 * released under an MIT-style license.
 */

String.SCRIPT_FRAGMENT = '<script[^>]*>([\\S\\s]*?)<\/script>';

JS.extend(String.prototype, /** @scope String.prototype */{
    
    /**
     * <p>Returns an array containing the content of any <tt>&lt;script&gt;</tt> tags present
     * in the string.</p>
     * @returns {Array}
     */
    extractScripts: function() {
        var matchAll = new RegExp(String.SCRIPT_FRAGMENT, 'img');
        var matchOne = new RegExp(String.SCRIPT_FRAGMENT, 'im');
        return (this.match(matchAll) || []).map(function(scriptTag) {
            return (scriptTag.match(matchOne) || ['', ''])[1];
        });
    },
    
    /**
     * <p>Extracts the content of any <tt>&lt;script&gt;</tt> tags present in the string and
     * <tt>eval</tt>s them. Returns an array containing the return value of each evaluated
     * script.</p>
     */
    evalScripts: function() {
        return this.extractScripts().map(function(script) { return eval(script); });
    },
    
    /**
     * <p>Returns the result of parsing the string as JSON. Requires the YUI JSON utility.</p>
     * @returns {Object|Array}
     */
    parseJSON: function() {
        return YAHOO.lang.JSON.parse(this.valueOf());
    },
    
    /**
     * <p>Returns a copy of the string with all &lt;script&gt; tags removed.</p>
     * @returns {String}
     */
    stripScripts: function() {
        return this.replace(new RegExp(String.SCRIPT_FRAGMENT, 'img'), '');
    },
    
    /**
     * <p>Returns a copy of the string with all HTML tags removed.</p>
     * @returns {String}
     */
    stripTags: function() {
        return this.replace(/<\/?[^>]+>/gi, '').trim();
    },
    
    /**
     * <p>Returns a copy of the string with all leading and trailing whitespace removed.</p>
     * @returns {String}
     */
    trim: YAHOO.lang.trim.methodize()
});

/**
 * @overview
 * <p>Ojay adds all the single-number functions in <tt>Math</tt> as methods to <tt>Number</tt>.
 * The following methods can all be called on numbers:</p>
 *
 * <pre><code>abs, acos, asin, atan, ceil, cos, exp, floor, log, pow, round, sin, sqrt, tan</code></pre>
 */
'abs acos asin atan ceil cos exp floor log pow round sin sqrt tan'.split(/\s+/).
        forEach(function(method) {
            Number.prototype[method] = Math[method].methodize();
        });

/**
 * <p>Calls the given <tt>block</tt> in the scope of <tt>context</tt> a given number of
 * times. The block receives the iteration index each time it is called.</p>
 * @param {Function} block
 * @param {Object} context
 */
Number.prototype.times = function(block, context) {
    if (this < 0) return;
    for (var i = 0; i < this; i++) block.call(context || null, i);
};

/**
 * <p>Returns <tt>true</tt> iff the number is between <tt>a</tt> and <tt>b</tt> inclusive.
 * To test the range without including the end points, pass <tt>false</tt> as the third
 * argument.</p>
 * @param {Number} a
 * @param {Number} b
 * @param {Boolean} inclusive
 * @returns {Boolean}
 */
Number.prototype.between = function(a, b, inclusive) {
    if (this > a && this < b) return true;
    return (this == a || this == b) ? (inclusive !== false) : false;
};

/**
 * Copyright (c) 2007-2008 James Coglan
 * http://blog.jcoglan.com/reiterate/
 * 
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 * 
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 * 
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */

Function.from = function(iterator) {
  if (iterator.toFunction) return iterator.toFunction();
  if (typeof iterator == 'function') return iterator;
  if (typeof iterator == 'object') return Function.fromObject(iterator);
  return function(x) { return x; };
};

String.prototype.toFunction = function() {
  var properties = this.split('.');
  if (!properties[0]) return function(x) { return x; };
  return function(o) {
    var object, member = o, key;
    for (var i = 0, n = properties.length; i < n; i++) {
      key = properties[i];
      object = member;
      member = object[key];
      if (typeof member == 'function') member = member.apply(object);
    }
    return member;
  };
};

Array.prototype.toFunction = function() {
  var method = this[0], args = this.slice(1);
  if (!method) return function(x) { return x; };
  return function(o) {
    var fn = (typeof method == 'function') ? method : o[method];
    return (typeof fn == 'function') ? fn.apply(o, args) : undefined;
  };
};

Function.fromObject = function(object) {
  var keys = [];
  for (var field in object) { if (object.hasOwnProperty(field)) keys.push(field); }
  if (keys.length === 0) return function(x) { return x; };
  return function(o) {
    var result = true, key, fn, args;
    for (var i = 0, n = keys.length; i < n; i++) {
      key = keys[i];
      fn = o[key]; args = object[key];
      if (typeof fn == 'function' && !(args instanceof Array)) args = [args];
      result = result && ((typeof fn == 'function') ? fn.apply(o, args) : fn == args);
    }
    return result;
  };
};

'filter forEach every map some'.split(/\s+/).forEach(function(method) {
  this[method] = this[method].wrap(function(fn, iterator, thisObject) {
    if (iterator) iterator = Function.from(iterator);
    return fn(iterator, thisObject);
  });
}, Array.prototype);

(function(Event) {
    JS.extend(Ojay, /** @scope Ojay */{
        /**
         * <p>Pre-built callback that stops the default browser reaction to an event.</p>
         * @param {DomCollection} element
         * @param {Event} evnt
         */
        stopDefault: function(element, evnt) {
            Event.preventDefault(evnt);
        },
        
        /**
         * <p>Pre-built callback that stops the event bubbling up the DOM tree.</p>
         * @param {DomCollection} element
         * @param {Event} evnt
         */
        stopPropagate: function(element, evnt) {
            Event.stopPropagation(evnt);
        },
        
        /**
         * <p>Pre-built callback that both stops the default behaviour and prevents bubbling.</p>
         * @param {DomCollection} element
         * @param {Event} evnt
         */
        stopEvent: function(element, evnt) {
            Ojay.stopDefault(element, evnt);
            Ojay.stopPropagate(element, evnt);
        },
        
        /**
         * <p>Returns an event callback that checks the event target against each given CSS
         * selector and fires all the applicable callbacks. Based on prior ideas from:</p>
         *
         * <ul>
         *     <li>http://icant.co.uk/sandbox/eventdelegation/</li>
         *     <li>http://www.danwebb.net/2008/2/8/event-delegation-made-easy-in-jquery</li>
         * </ul>
         *
         * <p>To delegate events, supply an object mapping CSS selectors to callback functions.
         * when the event fires, the target is compared against all given selectors all all
         * applicable callbacks are fired. If the secord parameter is set to <tt>true</tt>,
         * the delegator will crawl back up the DOM tree until it finds an element that contains
         * the target and matches the given selector.</p>
         *
         * @param {Object} map
         * @param {Boolean} includeAncestors
         * @returns {Function}
         */
        delegateEvent: function(map, includeAncestors) {
            return function(element, evnt) {
                var target = evnt.getTarget(), candidate;
                for (var selector in map) {
                    if (!target.matches(selector) && !includeAncestors) continue;
                    candidate = target;
                    if (includeAncestors) while (candidate && !candidate.matches(selector)) {
                        candidate = Ojay(candidate.node.parentNode);
                        if (candidate.node == document.body) candidate = null;
                    }
                    if (candidate) Function.from(map[selector]).call(this, candidate, evnt);
                }
            };
        },
        
        _getTarget: function() { return Ojay(Event.getTarget(this)); }
    });
    
    Ojay.stopDefault.method     = Ojay.stopDefault.partial(null).methodize();
    Ojay.stopPropagate.method   = Ojay.stopPropagate.partial(null).methodize();
    Ojay.stopEvent.method       = Ojay.stopEvent.partial(null).methodize();
    
    ['onDOMReady', 'onContentReady', 'onAvailable'].forEach(function(method) {
        Ojay[method] = Event[method].bind(Event);
    });
})(YAHOO.util.Event);

/**
 * <p>The <tt>Ojay.Observable</tt> module extends the <tt>JS.Observable</tt> module with an
 * <tt>on()</tt> method that behaves similarly to <tt>DomCollection#on()</tt>, used for
 * monitoring DOM events. It uses <tt>addObserver()</tt> to set up an interface through
 * which an object may publish named events, and other objects can listen to such events,
 * just as for DOM events. Here's an example of a class that uses the module:</p>
 *
 * <pre><code>    var Player = new JS.Class({
 *         include: Ojay.Observable,
 *         
 *         play: function() {
 *             this.startTime = this.getTime();
 *             this.notifyObservers('start');
 *         },
 *         
 *         pause: function() {
 *             var elapsed = this.getTime() - this.startTime;
 *             this.notifyObservers('pause', elapsed);
 *         },
 *         
 *         getTime: function() {
 *             return Number(new Date()) / 1000;
 *         }
 *     });</code></pre>
 *
 * <p>The <tt>getTime()</tt> method simply returns the current timestamp in seconds. The
 * <tt>play()</tt> method records the current time and fires the <tt>start</tt> event by using
 * <tt>notifyObservers()</tt> to send a message to its observers. The <tt>pause()</tt>
 * method simply publishes a <tt>pause</tt> event that sends the elapsed time to any
 * listeners.</p>
 *
 * <p>Some client code to listen to one of these objects might look like this:</p>
 *
 * <pre><code>    var p = new Player();
 *     
 *     p.on('start', function(player) {
 *         alert(player.startTime);
 *     });
 *     
 *     p.on('pause', function(player, timeElapsed) {
 *         alert(timeElapsed);
 *     });</code></pre>
 *
 * <p>All listeners receive the object that fired the event as their first argument, and
 * any data published by said object with the event as the subsequent arguments. An optional
 * third argument to <tt>on()</tt> specifies the execution context of the listener function,
 * so for example:</p>
 *
 * <pre><code>    p.on('start', function() {
 *         // this === someObject
 *     }, someObject);</code></pre>
 *
 * <p>All calls to <tt>on()</tt> return a <tt>MethodChain</tt> object that, by default, will
 * fire on the object publishing the event, so the following:</p>
 *
 * <pre><code>    p.on('start').pause();</code></pre>
 *
 * <p>Will cause <tt>p</tt> to call its <tt>pause()</tt> method whenever its <tt>start</tt>
 * event is fired.</p>
 *
 * <p>For further information on this module, see the <tt>JS.Observable</tt> documentation at
 * http://jsclass.jcoglan.com/observable.html.</p>
 *
 * @module Observable
 */
Ojay.Observable = new JS.Module({
    include: JS.Observable,
    
    /**
     * @param {String} eventName
     * @param {Function} callback
     * @param {Object} scope
     * @returns {MethodChain}
     */
    on: function(eventName, callback, scope) {
        var chain = new JS.MethodChain;
        if (callback && typeof callback != 'function') scope = callback;
        this.addObserver(function() {
            var args = Array.from(arguments), message = args.shift();
            if (message != eventName) return;
            var receiver = (args[0]||{}).receiver || this;
            if (typeof callback == 'function') {
                if (receiver !== this) args.shift();
                callback.apply(scope || null, [receiver].concat(args));
            }
            chain.fire(scope || receiver);
        }, this);
        return chain;
    }
});

(function(Ojay, Dom) {
    /**
     * <p>Wraps collections of DOM element references with an API for manipulation of page
     * elements. Includes methods for getting/setting class names and style attributes,
     * traversing the DOM, setting up event handlers, and performing animation.</p>
     * @constructor
     * @class DomCollection
     */
    Ojay.DomCollection = new JS.Class(/** @scope Ojay.DomCollection.prototype */{
        
        /**
         * @param {Array} collection
         * @returns {DomCollection}
         */
        initialize: function(collection) {
            this.length = 0;
            for (var i = 0, n = collection.length, nodeType, push = [].push; i < n; i++) {
                nodeType = collection[i].nodeType;
                if (nodeType === Ojay.HTML.ELEMENT_NODE ||
                    nodeType === Ojay.HTML.DOCUMENT_NODE ||
                    collection[i] == window)
                    push.call(this, collection[i]);
            }
            this.node = this[0];
            return this;
        },
        
        /**
         * <p>Returns the elements of the collection as a native Array type. Can optionally take
         * a function to convert values as the new array is constructed.</p>
         * @param {Function} via
         * @returns {Array}
         */
        toArray: function(via) {
            if (via) via = Function.from(via);
            var results = [], i, n = this.length;
            for (i = 0; i < n; i++) results.push(via ? via(this[i]) : this[i]);
            return results;
        },
        
        /**
         * <p> Returns a <tt>DomCollection</tt> wrapping the <tt>n</tt>th element in the current
         * collection.</p>
         * @param {Number} n
         * @returns {DomCollection}
         */
        at: function(n) {
            n = Number(n).round();
            var item = (n >= 0 && n < this.length) ? [this[n]] : [];
            return new this.klass(item);
        },
        
        /**
         * <p>Registers event listeners on all the members of the collection. You must supply at
         * least the name of the event to listen for, and you can supply a callback function and
         * (optionally) its scope as well. This method returns a <tt>MethodChain</tt> so you can
         * write more sentence-like code without needing to write explicit callback functions. Some
         * examples:</p>
         *
         * <pre><code>    Ojay('p').on('click').setStyle({textDecoration: 'underline'});
         *     
         *     Ojay('p').on('mouseout').hide().parents().setStyle( ... );
         *     
         *     Ojay('li').on('click')._('h1#title').setStyle({color: '#f00'});</code></pre>
         *
         * <p>When using chaining like this, the method chain is fired only on the element that
         * triggers each event, not on the whole collection you called <tt>on()</tt> on.</p>
         *
         * <p>When using explicit callback functions, the callback receives on <tt>Ojay</tt> object
         * wrapping the element that triggered the event, and the event object as arguments. If you
         * supply your own scope parameter, <tt>this</tt> refers to your supplied object inside the
         * callback.</p>
         *
         * <pre><code>    Ojay('div').on('click', function(element, ev) {
         *         // 'this' does not refer to anything useful
         *     });
         *     
         *     Ojay('p').on('mouseout', function(element, ev) {
         *         // 'this' refers to the object 'someObject'
         *     }, someObject);</code></pre>
         *
         * <p>Even when you supply an explicit function, <tt>on()</tt> returns a <tt>MethodChain</tt>
         * so you can use the chaining feature as well. You can store a reference to this collector
         * so you can modify the event handler at a later time, <em>without actually creating any new
         * handlers</em>:</p>
         *
         * <pre><code>    var chain = Ojay('a.external').on('click');
         *
         *     // somewhere else...
         *     chain.addClass('clicked');</code></pre>
         *
         * <p>Any <tt>a.external</tt> will then gain the class name when it is clicked.</p>
         *
         * <p>There is one final subtlety: if you supply a second argument that is NOT a function, it
         * will be used as the base object for any chain firings. e.g.:</p>
         *
         * <pre><code>    // When these &lt;p&gt;s are clicked, the &lt;h1&gt; changes
         *     Ojay('p.changer').on('click', Ojay('h1')).setStyle({textTransform: 'uppercase'})</code></pre>
         *
         *
         * <p>Ojay gives you easy control of how the browser should respond to events. Inside your
         * callback function, you can prevent the event's default behaviour and stop it bubbling up
         * the DOM like so:</p>
         *
         * <pre><ocde>    Ojay('a').on('click', function(element, ev) {
         *         ev.stopDefault();
         *         // ... your custom behaviour
         *     });</code></pre>
         *
         * <p><tt>stopDefault</tt> stops the browser running the default behaviour for the event, e.g.
         * loading a new page when a link is clicked. The method <tt>stopPropagate</tt> stops the
         * event bubbling, and <tt>stopEvent</tt> does both. If all your callback does is call one
         * of these methods, you can use on of Ojay's pre-stored callbacks instead:</p>
         *
         * <pre><code>    Ojay('a').on('click', Ojay.stopDefault).setStyle({textDecoration: 'underline'});</code></pre>
         *
         * <p>You can use <tt>stopDefault</tt>, <tt>stopPropagate</tt> and <tt>stopEvent</tt> in this
         * manner. Using these is recommended over writing your own callbacks to do this, as creating
         * new identical functions wastes memory.</p>
         *
         * @param {String} eventName
         * @param {Function} callback
         * @param {Object} scope
         * @returns {MethodChain}
         */
        on: function(eventName, callback, scope) {
            var chain = new JS.MethodChain;
            if (callback && typeof callback != 'function') scope = callback;
            YAHOO.util.Event.on(this, eventName, function(evnt) {
                var wrapper = Ojay(this);
                evnt.stopDefault   = Ojay.stopDefault.method;
                evnt.stopPropagate = Ojay.stopPropagate.method;
                evnt.stopEvent     = Ojay.stopEvent.method;
                evnt.getTarget     = Ojay._getTarget;
                if (typeof callback == 'function') callback.call(scope || null, wrapper, evnt);
                chain.fire(scope || wrapper);
            });
            return chain;
        },
        
        /**
         * <p>Runs an animation on all the elements in the collection. The method expects you to supply
         * at least an object specifying CSS properties to animate, and the duration of the animation.</p>
         *
         * <pre><code>   Ojay('#some-list li').animate({marginLeft: {to: 200}}, 1.5)</code></pre>
         *
         * <p>Functions can be used for any of these values to apply a different animation to each element
         * in the collection. Each function is passed the element's position in the collection (<tt>i</tt>)
         * and the element itself (<tt>el</tt>), and is evaluated just before the animation begins. <tt>el</tt>
         * is actually a <tt>DomCollection</tt> wrapping a single element. For example, to animate some
         * list elements out by a staggered amount, do:</p>
         *
         * <pre><code>   Ojay('#some-list li').animate({
         *        marginLeft: {
         *            to: function(i, el) { return 40 * i; }
         *        }
         *    }, 2.0);</code></pre>
         *
         * <p>The functions can appear at any level of the <tt>parameters</tt> object, so you could write
         * the above as:</p>
         *
         * <pre><code>   Ojay('#some-list li').animate(function(i, el) {
         *        return {
         *            marginLeft: {to: 40 * i}
         *        };
         *    }, 2.0);</code></pre>
         *
         * <p>or</p>
         *
         * <pre><code>   Ojay('#some-list li').animate({
         *        marginLeft: function(i, el) {
         *            return {to: 40 * i};
         *        }
         *    }, 2.0);</code></pre>
         *
         * <p>This allows for highly flexible animation definitions. You can also specify a function as
         * the <tt>duration</tt> parameter, so that each element takes a different time to animate:</p>
         *
         * <pre><code>   Ojay('#some-list li').animate({marginLeft: {to: 200}},
         *            function(i) { return 0.5 + 2.0 * (i/5).sin().abs(); });</code></pre>
         *
         * <p>The final parameter, <tt>options</tt>, allows you to specify various optional arguments to
         * control the animation. They are:</p>
         *
         * <p><tt>easing</tt>: The easing function name (from <tt>YAHOO.util.Easing</tt>) to control the
         * flow of the animation. Default is <tt>'easeBoth'</tt>.</p>
         *
         * <p><tt>after</tt>: A function to be called for each memeber of the collection when it finishes
         * its animation. The function receives the element and its position in the list as arguments.</p>
         *
         * <p>An example:</p>
         *
         * <pre><code>   Ojay('#some-list li').animate({marginLeft: {to: 40}}, 5.0, {easing: 'elasticOut'});</code></pre>
         *
         * @param {Object|Function} parameters
         * @param {Number|Function} duration
         * @param {Object} options
         * @returns {MethodChain}
         */
        animate: function(parameters, duration, options) {
            var animation = new Ojay.Animation(this, parameters, duration, options);
            animation.run();
            return animation.chain;
        },
        
        /**
         * <p>Adds the given string as a class name to all the elements in the collection and returns
         * a reference to the collection for chaining.</p>
         * @param {String} className
         * @returns {DomCollection}
         */
        addClass: function(className) {
            Dom.addClass(this, className);
            return this;
        },
        
        /**
         * <p>Removes the given class name(s) from all the elements in the collection and returns a
         * reference to the collection for chaining.</p>
         * @param {String} className
         * @returns {DomCollection}
         */
        removeClass: function(className) {
            Dom.removeClass(this, className);
            return this;
        },
        
        /**
         * <p>Replaces <tt>oldClass</tt> with <tt>newClass</tt> for every element in the collection
         * and returns a reference to the collection for chaining.</p>
         * @param {String} oldClass
         * @param {String} newClass
         * @returns {DomCollection}
         */
        replaceClass: function(oldClass, newClass) {
            Dom.replaceClass(this, oldClass, newClass);
            return this;
        },
        
        /**
         * <p>Sets the class name of all the elements in the collection to the given value and
         * returns a reference to the collection for chaining.</p>
         * @param {String} className
         * @returns {DomCollection}
         */
        setClass: function(className) {
            return this.setAttributes({className: className});
        },
        
        /**
         * <p>Returns true iff the first member of the collection has the given class name.</p>
         * @param {String} className
         * @returns {Boolean}
         */
        hasClass: function(className) {
            if (!this.node) return undefined;
            return Dom.hasClass(this.node, className);
        },
        
        /**
         * <p>Returns the value of the named style property for the first element in the collection.</p>
         * @param {String} name
         * @returns {String}
         */
        getStyle: function(name) {
            if (!this.node) return undefined;
            return Dom.getStyle(this.node, String(name));
        },
        
        /**
         * <p>Sets the style of all the elements in the collection using a series of key/value pairs.
         * Keys correspond to CSS style property names, and should be camel-cased where they would
         * be hyphentated in stylesheets. Returns the <tt>DomCollection</tt> instance for chaining.
         * You need to use a string key for <tt>'float'</tt> as it's a reserved word in JavaScript.</p>
         *
         * <pre><code>    Ojay('p').setStyle({color: '#f00', fontSize: '14px', 'float': 'left'});</code></pre>
         *
         * @param {Object} options
         * @returns {DomCollection}
         */
        setStyle: function(options) {
            var value, isIE = !!YAHOO.env.ua.ie;
            for (var property in options) {
                if (isIE && property == 'opacity') {
                    value = Number(options[property]);
                    if (value === 0) options[property] = 0.001;
                    if (value === 1) {
                        Dom.setStyle(this, 'filter', '');
                        continue;
                    }
                }
                Dom.setStyle(this, property, options[property]);
            }
            return this;
        },
        
        /**
         * <p>Sets the given HTML attributes of all the elements in the collection, and returns the
         * collection for chaining. Remember to use <tt>className</tt> for classes, and <tt>htmlFor</tt>
         * for label attributes.</p>
         *
         * <pre><code>    Ojay('img').setAttributes({src: 'images/tom.png'});</code></pre>
         *
         * @param Object options
         * @returns DomCollection
         */
        setAttributes: function(options) {
            for (var i = 0, n = this.length; i < n; i++) {
                for (var key in options)
                    this[i][key] = options[key];
            }
            return this;
        },
        
        /**
         * <p>Hides every element in the collection and returns the collection.</p>
         * @returns {DomCollection}
         */
        hide: function() {
            return this.setStyle({display: 'none'});
        },
        
        /**
         * <p>Shows/unhides every element in the collection and returns the collection.</p>
         * @returns {DomCollection}
         */
        show: function() {
            return this.setStyle({display: ''});
        },
        
        /**
         * <p>If <tt>html</tt> is a string, sets the <tt>innerHTML</tt> of every element in the
         * collection to the given string value. If <tt>html</tt> is an <tt>HTMLElement</tt>, inserts
         * the element into the first item in the collection (inserting DOM nodes multiple times just
         * moves them from place to place).</p>
         * @param {String|HTMLElement} html
         * @returns {DomCollection}
         */
        setContent: function(html) {
            if (!this.node) return this;
            if (html instanceof this.klass) html = html.node;
            if (html && html.nodeType === Ojay.HTML.ELEMENT_NODE) {
                this.node.innerHTML = '';
                this.node.appendChild(html);
            } else {
                this.forEach(function(element) {
                    element.node.innerHTML = '';
                    element.insert(html, 'bottom');
                });
            }
            return this;
        },
        
        /**
         * <p>Inserts the given <tt>html</tt> (a <tt>String</tt> or an <tt>HTMLElement</tt>) into every
         * element in the collection at the given <tt>position</tt>. <tt>position</tt> can be one of
         * <tt>'top'</tt>, <tt>'bottom'</tt>, <tt>'before'</tt> or <tt>'after'</tt>, and it defaults to
         * <tt>'bottom'</tt>. Returns the <tt>DomCollection</tt> for chaining.</p>
         *
         * <p>If you supply an <tt>HTMLElement</tt> then it will only be inserted into the first element
         * of the collection; inserting an element multiple times simply moves it around the document.
         * If you want multiple insertions, you should clone the element yourself. Ojay does not clone it
         * for you as this removes event handlers you may have registered with the element.</p>
         *
         * <pre><code>    Ojay('#someDiv').insert('&lt;p&gt;Inserted after the DIV&lt;/p&gt;', 'after');
         *     
         *     Ojay('ul li').insert(Ojay.HTML.span({className: 'foo'}, 'Item: '), 'top');</code></pre>
         *
         * @param {String|HTMLElement} html
         * @param {String} position
         * @returns {DomCollection}
         */
        insert: function(html, position) {
            if (position == 'replace') return this.setContent(html);
            if (html instanceof this.klass) html = html.node;
            new Ojay.DomInsertion(this.toArray(), html, position);
            return this;
        },
        
        /**
         * <p>Removes all the elements in the collection from the document, and returns the collection.</p>
         * @returns {DomCollection}
         */
        remove: function() {
            this.toArray().forEach(function(element) {
                if (element.parentNode)
                    element.parentNode.removeChild(element);
            });
            return this;
        },
        
        /**
         * <p>Returns true iff the first element in the collection matches the given CSS selector.</p>
         * @param {String} selector
         * @returns {Boolean}
         */
        matches: function(selector) {
            if (!this.node) return undefined;
            return YAHOO.util.Selector.test(this.node, selector);
        },
        
        /**
         * <p>Returns a new <tt>DomCollection</tt> containing the elements of the collection
         * that match the selector if one is given.</p>
         * @param {String} selector
         * @returns {DomCollection}
         */
        query: function(selector, array) {
            var collection = array ? Ojay(array) : this;
            if (!selector) return new this.klass(collection.toArray());
            collection = collection.filter({matches: selector});
            return new this.klass(collection.toArray());
        },
        
        /**
         * <p>Returns a new <tt>DomCollection</tt> of the unique parent nodes of all the elements
         * in the collection. If a selector string is supplied, only elements that match the
         * selector are included.</p>
         * @param {String} selector
         * @returns {DomCollection}
         */
        parents: function(selector) {
            var parents = this.toArray('parentNode');
            return this.query(selector, parents.unique());
        },
        
        /**
         * <p>Returns a new <tt>DomCollection</tt> of the unique ancestor nodes of all the elements
         * in the collection. If a selector string is supplied, only elements that match the
         * selection are included.</p>
         * @param {String} selector
         * @returns {DomCollection}
         */
        ancestors: function(selector) {
            var ancestors = [];
            this.toArray().forEach(function(element) {
                while ((element.tagName.toLowerCase() != 'body') && (element = element.parentNode)) {
                    if (ancestors.indexOf(element) == -1)
                        ancestors.push(element);
                }
            });
            return this.query(selector, ancestors);
        },
        
        /**
         * <p>Returns a new <tt>DomCollection</tt> of the unique child nodes of all the elements
         * in the collection. If a selector string is supplied, only elements that match the
         * selection are included.</p>
         * @param {String} selector
         * @returns {DomCollection}
         */
        children: function(selector) {
            var children = [];
            this.toArray().forEach(function(element) {
                var additions = Dom.getChildren(element), arg;
                while (arg = additions.shift()) {
                    if (children.indexOf(arg) == -1)
                        children.push(arg);
                }
            });
            return this.query(selector, children);
        },
        
        /**
         * <p>Returns a new <tt>DomCollection</tt> of the unique descendant nodes of all the elements
         * in the collection. If a selector string is supplied, only elements that match the
         * selection are included.</p>
         * @param {String} selector
         * @returns {DomCollection}
         */
        descendants: function(selector) {
            selector = selector || '*';
            var descendants = [];
            this.toArray().forEach(function(element) {
                var additions = Ojay.query(selector, element), arg;
                while (arg = additions.shift()) {
                    if (descendants.indexOf(arg) == -1)
                        descendants.push(arg);
                }
            });
            return new this.klass(descendants);
        },
        
        /**
         * <p>Returns a new <tt>DomCollection</tt> of the unique siblings of all the elements in the
         * collection. The returned collection does not include elements present in the original
         * collection. If a selector string is supplied, only elements that match the selection are
         * included.</p>
         * @param {String} selector
         * @returns {DomCollection}
         */
        siblings: function(selector) {
            var these = this.toArray(), siblings = [];
            these.forEach(function(element) {
                var additions = Ojay(element).parents().children(selector).toArray(), arg;
                while (arg = additions.shift()) {
                    if ((these.indexOf(arg) == -1) && (siblings.indexOf(arg) == -1))
                        siblings.push(arg);
                }
            });
            return new this.klass(siblings);
        },
        
        /**
         * <p>Returns a <tt>Region</tt> object representing the rectangle occupied by the the first
         * element in the collection.</p>
         * @returns {Region}
         */
        getRegion: function() {
            if (!this.node) return undefined;
            return new Ojay.Region(Dom.getRegion(this.node));
        },
        
        /**
         * <p>Resizes every member of the collection so as to fit inside the given region exactly.</p>
         * @param {Region} region
         * @returns {DomCollection}
         */
        fitToRegion: function(region) {
            var width = region.getWidth(), height = region.getHeight();
            this.forEach(function(element) {
                element.setStyle({width: width + 'px', height: height + 'px'});
                var reg = element.getRegion(), w = reg.getWidth(), h = reg.getHeight();
                element.setStyle({width: (2 * width - w) + 'px', height: (2 * height - h) + 'px'});
            });
            return this;
        },
        
        /**
         * <p>Returns the total width of the region occupied by the element, including padding
         * and borders. Values returned are in pixels.</p>
         * @returns {Number}
         */
        getWidth: function() {
            if (!this.node) return undefined;
            return this.getRegion().getWidth();
        },
        
        /**
         * <p>Returns the total height of the region occupied by the element, including padding
         * and borders. Values returned are in pixels.</p>
         * @returns {Number}
         */
        getHeight: function() {
            if (!this.node) return undefined;
            return this.getRegion().getHeight();
        },
        
        /**
         * <p>Returns the position of the top edge of the first element in the collection relative
         * to the viewport, in pixels.</p>
         * @returns {Number}
         */
        getTop: function() {
            if (!this.node) return undefined;
            return this.getRegion().top;
        },
        
        /**
         * <p>Returns the position of the bottom edge of the first element in the collection relative
         * to the viewport, in pixels.</p>
         * @returns {Number}
         */
        getBottom: function() {
            if (!this.node) return undefined;
            return this.getRegion().bottom;
        },
        
        /**
         * <p>Returns the position of the left edge of the first element in the collection relative
         * to the viewport, in pixels.</p>
         * @returns {Number}
         */
        getLeft: function() {
            if (!this.node) return undefined;
            return this.getRegion().left;
        },
        
        /**
         * <p>Returns the position of the right edge of the first element in the collection relative
         * to the viewport, in pixels.</p>
         * @returns {Number}
         */
        getRight: function() {
            if (!this.node) return undefined;
            return this.getRegion().right;
        },
        
        /**
         * <p>Returns the position of the center of the element as an object with <tt>left</tt> and
         * <tt>top</tt> properties. Values returned are in pixels.</p>
         * @returns {Object}
         */
        getCenter: function() {
            if (!this.node) return undefined;
            return this.getRegion().getCenter();
        },
        
        /**
         * <p>Returns true iff the first element in the collection intersects the area of the element
         * given as an argument.</p>
         * @param {String|HTMLElement|DomCollection} element
         * @returns {Boolean}
         */
        areaIntersects: function(element) {
            if (!this.node) return undefined;
            var node = Ojay(element);
            return this.getRegion().intersects(node.getRegion());
        },
        
        /**
         * <p>Returns a <tt>Region</tt> representing the overlapping region of the first element in the
         * collection and the argument.</p>
         * @param {String|HTMLElement|DomCollection} element
         * @returns {Region}
         */
        intersection: function(element) {
            if (!this.node) return undefined;
            var node = Ojay(element);
            var A = this.getRegion(), B = node.getRegion();
            return A.intersects(B) ? A.intersection(B) : null;
        },
        
        /**
         * <p>Returns true iff the first element in the collection completely contains the area of the
         * element given as an argument.</p>
         * @param {String|HTMLElement|DomCollection} element
         * @returns {Boolean}
         */
        areaContains: function(element) {
            if (!this.node) return undefined;
            var node = Ojay(element);
            return this.getRegion().contains(node.getRegion());
        }
    });
})(Ojay, YAHOO.util.Dom);

(function() {
    var methods = {};
    for (var method in Ojay.ARRAY_METHODS) (function(name) {
        var noConvert = /^(?:indexOf|lastIndexOf|unique)$/.test(name);
        methods[name] = function() {
            var array = noConvert ? this.toArray() : this.toArray(Ojay);
            var result = array[name].apply(array, arguments);
            if (name == 'filter')
                result = Ojay(result.map(function(el) { return el.node; }));
            return result;
        };
    })(method);
    Ojay.DomCollection.include(methods);
})();

Ojay.fn = Ojay.DomCollection.prototype;

/**
 * <p>The <tt>DomInsertion</tt> class is used to insert new strings and elements into the DOM.
 * It should not be used as a public API; you should use <tt>DomCollection</tt>'s <tt>insert</tt>
 * method instead. Its implementation is based on <a href="http://prototypejs.org/api/element/insert">that
 * used by Prototype</a>.</p>
 *
 * Document insertion code: Copyright (c) 2005-2008 Sam Stephenson / the Prototype team,
 * released under an MIT-style license.
 *
 * @contructor
 * @class DomInsertion
 */
Ojay.DomInsertion = new JS.Class(/** @scope Ojay.DomInsertion.prototype */{
    
    /**
     * @param {Array|HTMLElement} elements
     * @param {String|HTMLElement} html
     * @param {String} position
     */
    initialize: function(elements, html, position) {
        if (!(elements instanceof Array)) elements = [elements];
        if (!(/^(?:top|bottom|before|after)$/i.test(position))) position = 'bottom';
        
        this._elements = elements.filter(function(el) { return el && el.nodeType === Ojay.HTML.ELEMENT_NODE; });
        this._html = html;
        this._position = position.toLowerCase();
        
        if (this._elements.length === 0) return;
        if (this._html && this._html.nodeType) this._insertElement();
        if (typeof this._html == 'string') this._insertString();
    },
    
    /**
     * <p>Performs insertion of <tt>HTMLElement</tt>s.</p>
     */
    _insertElement: function() {
        var insert = this.klass._TRANSLATIONS[this._position];
        this._elements.forEach(function(element) {
            insert(element, this._html);
        }, this);
    },
    
    /**
     * <p>Performs insertion of <tt>String</tt>s.</p>
     */
    _insertString: function() {
        var insert = this.klass._TRANSLATIONS[this._position];
        this._elements.forEach(function(element) {
            var tagName = (/^(?:before|after)$/.test(this._position) ? element.parentNode : element).tagName.toUpperCase();
            var childNodes = this._getContentFromElement(tagName);
            if (/^(?:top|after)$/.test(this._position)) childNodes.reverse();
            childNodes.forEach(insert.partial(element));
        }, this);
    },
    
    /**
     * <p>Returns a collection of nodes by creating a new DIV and using <tt>innerHTML</tt>
     * to create the elements. Used when inserting into table elements and SELECT boxes,
     * which don't allow <tt>innerHTML</tt>modifications quite like everything else.</p>
     * @param {String} tagName
     * @returns {Array}
     */
    _getContentFromElement: function(tagName) {
        var tag = this.klass._TAGS[tagName];
        var div = Ojay.HTML.div();
        if (tag) {
            div.innerHTML = tag[0] + this._html + tag[1];
            for (var i = 0, n = tag[2]; i < n; i++)
                div = div.firstChild;
        } else div.innerHTML = this._html;
        return Array.from(div.childNodes);
    },
    
    extend: /** @scope Ojay.DomInsertion */{
        
        /**
         * <p>Collection of definitions for how to perform insertions of strings and elements at
         * various positions.</p>
         */
        _TRANSLATIONS: {
            
            top: function(element, html) {
                element.insertBefore(html, element.firstChild);
            },
            
            bottom: function(element, html) {
                element.appendChild(html);
            },
            
            before: function(element, html) {
                element.parentNode.insertBefore(html, element);
            },
            
            after: function(element, html) {
                element.parentNode.insertBefore(html, element.nextSibling);
            }
        },
        
        /**
         * <p>Tags that need special treatment when trying to use <tt>innerHTML</tt>.</p>
         */
        _TAGS: {
            TABLE:  ['<table>',                '</table>',                   1],
            THEAD:  ['<table><tbody>',         '</tbody></table>',           2],
            TBODY:  ['<table><tbody>',         '</tbody></table>',           2],
            TFOOT:  ['<table><tbody>',         '</tbody></table>',           2],
            TR:     ['<table><tbody><tr>',     '</tr></tbody></table>',      3],
            TD:     ['<table><tbody><tr><td>', '</td></tr></tbody></table>', 4],
            TH:     ['<table><tbody><tr><td>', '</td></tr></tbody></table>', 4],
            SELECT: ['<select>',               '</select>',                  1]
        }
    }
});

/**
 * <p>Sane DOM node creation API, inspired by
 * <a href="http://api.rubyonrails.org/classes/Builder/XmlMarkup.html"><tt>Builder::XmlMarkup</tt></a>
 * in Ruby on Rails.</p>
 *
 * <p>This class lets you use a much nicer syntax for creating DOM nodes, without resorting to
 * <tt>document.createElement</tt> and friends. Essentially, you write JavaScript that mirrors
 * the HTML you're creating. The methods in the class return <tt>HTMLElement</tt> objects rather
 * than strings of HTML.</p>
 *
 * <p>To begin, you create a new <tt>HtmlBuilder</tt>:</p>
 *
 * <pre><code>    var html = new Ojay.HtmlBuilder();</code></pre>
 *
 * <p>Then write your HTML. Use hashes for tag attributes, strings for text nodes, and functions
 * to nest further tags inside the current node. The beauty of this is that you can easily add
 * whatever logic you want inside the functions to customize the HTML generated. A simple example:</p>
 *
 * <pre><code>    var div = html.div({id: 'container'}, function(html) {
 *         html.h1('This is the title');
 *         html.p({className: 'para'}, 'Lorem ipsum dolor sit amet...');
 *         html.ul(function(html) {
 *             ['One', 'Two', 'Three'].forEach(html.method('li'));
 *         });
 *     });</code></pre>
 *
 * <p>Now <tt>div</tt> is an <tt>HTMLElement</tt> object with the following structure:</p>
 *
 * <pre><code>    &lt;div id="container"&gt;
 *         &lt;h1&gt;This is the title&lt;/h1&gt;
 *         &lt;p class="para"&gt;Lorem ipsum dolor sit amet...&lt;/p&gt;
 *         &lt;ul&gt;
 *             &lt;li&gt;One&lt;/li&gt;
 *             &lt;li&gt;Two&lt;/li&gt;
 *             &lt;li&gt;Three&lt;/li&gt;
 *         &lt;/ul&gt;
 *     &lt;/div&gt;</code></pre>
 *
 * <p>If you prefer, there is a pre-initialized instance of <tt>HtmlBuilder</tt> named
 * <tt>Ojay.HTML</tt>. So, you can call <tt>Ojay.HTML.div('DIV content')</tt> and the like.</p>
 *
 * <p>One key advantage of writing HTML out using JavaScript is that you can assign references
 * to elements as they are being created, without needing to add IDs or class names to them for
 * later reference. For example:</p>
 *
 * <pre><code>    var FormController = new JS.Class({
 *         
 *         initialize: function(element) {
 *             element = Ojay(element);
 *             var self = this;
 *             var form = Ojay.HTML.form(function(html) {
 *                 html.h3('Enter your email address');
 *                 html.label('Email:');
 *                 self.emailField = html.input({type: 'text'});
 *                 self.button = html.input({type: 'submit', value: 'Go!'});
 *             });
 *             this.form = Ojay(form);
 *             element.setContent(form);
 *             this.registerEventHandlers();
 *         },
 *         
 *         registerEventHandlers: function() {
 *             this.form.on('submit', function(e) {
 *                 alert(this.emailField.value);
 *             }, this);
 *         }
 *     });</code></pre>
 *
 * <p>Note how the <tt>emailField</tt> property is set at the same time that the element is
 * being created. Storing this reference means you don't have to crawl the DOM for the right
 * node later on, so performance is improved. Also, the fact that you don't need to add IDs
 * or class names to the new elements means you've less chance of causing a naming collision
 * with existing page elements, or unintentionally inheriting stylesheet rules.</p>
 *
 * <p>All the tags defined in the HTML 4.01 spec are available in <tt>HtmlBuilder</tt>. You can
 * see which tags are implemented by inspecting the array <tt>Ojay.HtmlBuilder.TAG_NAMES</tt>.</p>
 *
 * @constructor
 * @class HtmlBuilder
 */
Ojay.HtmlBuilder = new JS.Class(/* @scope Ojay.HtmlBuilder.prototype */{
    
    /**
     * @param {HTMLElement} node
     */
    initialize: function(node) {
        this._rootNode = node || null;
    },
    
    /**
     * @param {HTMLElement} node
     */
    concat: function(node) {
        if (this._rootNode) this._rootNode.appendChild(node);
        return node;
    },
    
    extend: {
        addTagNames: function() {
            var args = (arguments[0] instanceof Array) ? arguments[0] : arguments;
            for (var i = 0, n = args.length; i < n; i++)
                this.addTagName(args[i]);
        },
        
        addTagName: function(name) {
            this.prototype[name] = function() {
                var node = document.createElement(name), arg, attr, style, appendable;
                loop: for (var j = 0, m = arguments.length; j < m; j++) {
                    arg = arguments[j];
                    
                    switch (typeof arg) {
                    case 'object':
                        appendable = arg.node || arg;
                        if (appendable.nodeType === Ojay.HTML.ELEMENT_NODE) {
                            node.appendChild(appendable);
                        } else {
                            for (attr in arg) {
                                if (Number(attr) == attr) continue;
                                if (attr == 'style')
                                    for (style in arg[attr]) node.style[style] = arg[attr][style];
                                else
                                    node[attr] = arg[attr];
                            }
                        }
                        break;
                        
                    case 'function': arg(new Ojay.HtmlBuilder(node));
                        break;
                        
                    case 'string': node.appendChild(document.createTextNode(arg));
                        break;
                    }
                }
                if (this._rootNode) this._rootNode.appendChild(node);
                return node;
            };
        },
        
        /**
         * List of all HTML 4.01 tag names, culled from the <a
         * href="http://www.w3.org/TR/REC-html40/index/elements.html">W3C spec</a>.
         */
        TAG_NAMES: (
            "a abbr acronym address applet area b base basefont bdo big blockquote body " +
            "br button caption center cite code col colgroup dd del dfn dir div dl dt em " +
            "embed fieldset font form frame frameset h1 h2 h3 h4 h5 h6 head hr html i " +
            "iframe img input ins isindex kbd label legend li link map menu meta noframes " +
            "noscript object ol optgroup option p param pre q s samp script select small " +
            "span strike strong style sub sup table tbody td textarea tfoot th thead title " +
            "tr tt u ul var"
        ).split(/\s+/)
    }
});

Ojay.HtmlBuilder.addTagNames(Ojay.HtmlBuilder.TAG_NAMES);

/**
 * <p>A pre-initialized instance of <tt>HtmlBuilder</tt>.</p>
 */
Ojay.HTML = new Ojay.HtmlBuilder();

/**
 *<p>Named references to all types of DOM node -- these are defined in Mozilla but not in IE.</p>
 */
JS.extend(Ojay.HTML, /** @scope Ojay.HTML */{
    ELEMENT_NODE:                   1,
    ATTRIBUTE_NODE:                 2,
    TEXT_NODE:                      3,
    CDATA_SECTION_NODE:             4,
    ENTITY_REFERENCE_NODE:          5,
    ENTITY_NODE:                    6,
    PROCESSING_INSTRUCTION_NODE:    7,
    COMMENT_NODE:                   8,
    DOCUMENT_NODE:                  9,
    DOCUMENT_TYPE_NODE:             10,
    DOCUMENT_FRAGMENT_NODE:         11,
    NOTATION_NODE:                  12
});

/**
 * @overview
 * <p>The <tt>Animation</tt> class is used to set up all animations in Ojay. It is entirely
 * for internal consumption, and not to be accessed directly. Use the <tt>animate</tt> method
 * in <tt>DomCollection</tt> instead, and look to that for documentation.</p>
 * @constructor
 * @class Animation
 */
Ojay.Animation = new JS.Class(/** @scope Ojay.Animation.prototype */{
    
    /**
     * @param {DomCollection} elements
     * @param {Object|Function} parameters
     * @param {Number|Function} duration
     * @param {Object} options
     */
    initialize: function(elements, parameters, duration, options) {
        this._collection        = elements;
        this._parameters        = parameters || {};
        this._duration          = duration || 1.0;
        this._options           = options || {};
        this._easing            = YAHOO.util.Easing[this._options.easing || 'easeBoth'];
        var after = this._options.after, before = this._options.before;
        this._afterCallback     = after && Function.from(after);
        this._beforeCallback    = before && Function.from(before);
        this.chain              = new JS.MethodChain;
    },
    
    /**
     * @param {Object|Function} options
     * @param {DomCollection} element
     * @param {Number} i
     * @returns {Object}
     */
    _evaluateOptions: function(options, element, i) {
        if (typeof options == 'function') options = options(i, element);
        if (typeof options != 'object') return options;
        var results = {};
        for (var field in options) results[field] = arguments.callee(options[field], element, i);
        return results;
    }.curry(),
    
    /**
     * <p>Runs the animation.</p>
     */
    run: function() {
        var paramSets = this._collection.map(this._evaluateOptions(this._parameters));
        var durations = this._collection.map(this._evaluateOptions(this._duration));
        
        var maxDuration = durations.reduce(function(a,b) { return a > b ? a : b; }, -Infinity);
        var callbackAttached = false;
        
        var after = this._afterCallback, before = this._beforeCallback;
        
        this._collection.forEach(function(element, i) {
            var parameters = paramSets[i], duration = durations[i];
            var anim = new YAHOO.util.ColorAnim(element.node, parameters, duration, this._easing);
            anim.onComplete.subscribe(function() {
                if (YAHOO.env.ua.ie && (parameters.opacity || {}).to !== undefined)
                    element.setStyle({opacity: parameters.opacity.to});
                
                if (after) after(element, i);
                
                if (duration == maxDuration && !callbackAttached) {
                    callbackAttached = true;
                    this.chain.fire(this._collection);
                }
            }.bind(this));
            if (before) before(element, i);
            anim.animate();
        }, this);
    }
});

(function(Region) {
    /**
     * <p>The <tt>Region</tt> class wraps YUI's <tt>Region</tt> class and extends its API. This
     * class is mostly for internal consumption: methods should exist on <tt>DomCollection</tt>
     * for getting the geometric properties of DOM elements.</p>
     * @constructor
     * @class Region
     */
    Ojay.Region = new JS.Class(/** @scope Ojay.Region.prototype */{
        
        contains:   Region.prototype.contains,
        getArea:    Region.prototype.getArea,
        _intersect: Region.prototype.intersect,
        _union:     Region.prototype.union,
        
        /**
         * @param {YAHOO.util.Region} region
         */
        initialize: function(region) {
            ['top', 'right', 'bottom', 'left'].forEach(function(property) {
                this[property] = region[property] || 0;
            }, this);
        },
        
        /**
         * @returns {Number}
         */
        getWidth: function() {
            return this.right - this.left;
        },
        
        /**
         * @returns {Number}
         */
        getHeight: function() {
            return this.bottom - this.top;
        },
        
        /**
         * @returns {Number}
         */
        getDiagonal: function() {
            return (this.getWidth().pow(2) + this.getHeight().pow(2)).sqrt();
        },
        
        /**
         * @returns {Object}
         */
        getCenter: function() {
            return {
                left: (this.left + this.right) / 2,
                top: (this.top + this.bottom) / 2
            };
        },
        
        /**
         * @param {Number} x
         * @param {Number} y
         * @returns {Region}
         */
        shift: function(x,y) {
            this.left += x;     this.right += x;
            this.top += y;      this.bottom += y;
            return this;
        },
        
        /**
         * @param {Number} factor
         * @returns {Region}
         */
        scale: function(factor) {
            var w = this.getWidth(), h = this.getHeight();
            if (w <= 0 || h <= 0) return this;
            var dx = (factor - 1) * w, dy = (factor - 1) * h;
            this.left -= dx/2;      this.right += dx/2;
            this.top -= dy/2;       this.bottom += dy/2;
            return this;
        },
        
        /**
         * @param {Region} region
         * @returns {Region}
         */
        intersection: function(region) {
            var intersection = this._intersect(region);
            return new Ojay.Region(intersection);
        },
        
        /**
         * <p>Returns <tt>true</tt> iff this region intersects the given region.</p>
         * @param {Region} region
         * @returns {Boolean}
         */
        intersects: function(region) {
            var top = Math.max(this.top, region.top),
                bottom = Math.min(this.bottom, region.bottom),
                left = Math.max(this.left, region.left),
                right = Math.min(this.right, region.right);
            return (top < bottom) && (left < right);
        },
        
        /**
         * @param {Region} region
         * @returns {Region}
         */
        union: function(region) {
            var union = this._union(region);
            return new Ojay.Region(union);
        },
        
        /**
         * @returns {String}
         */
        toString: function() {
            return '(' + this.left + ',' + this.top + ') [' + this.getWidth() + 'x' + this.getHeight() + ']';
        },
        
        extend: /** @scope Ojay.Region */{
            convert: function(object) {
                if (object instanceof Region) return new this(object);
                if (!(object instanceof this)) object = Ojay(object).getRegion();
                if (!object) return undefined;
                else return object;
            }
        }
    });
})(YAHOO.util.Region);

/**
 * <p>The <tt>Sequence</tt> class allows iteration over an array using a timer to
 * skip from member to member. At each timeframe, the sequence object calls a user-
 * defined callback function, passing in the current member (the 'needle') and its
 * position in the list.</p>
 * @constructor
 * @class Ojay.Sequence
 */
Ojay.Sequence = new JS.Class(/** @scope Ojay.Sequence.prototype */{
    
    /**
     * @param {Array} list
     * @param {Function} callback
     * @param {Object} context
     */
    initialize: function(list, callback, context) {
        this._list = list;
        this._counter = 0;
        this._callback = Function.from(callback);
        this._context = context || null;
        this._interval = null;
        this._looping = false;
        this._pauseOnComplete = false;
    },
    
    _fireCallback: function() {
        this._callback.call(this._context, this._list[this._counter]);
    },
    
    /**
     * <p>Calls the callback function on the current needle and steps the counter forward by
     * one place. When looping, sets a timeout to call itself again after the specified time.</p>
     * @returns {Sequence}
     */
    stepForward: function() {
        if (this._looping === null) {
            this._looping = false;
            return this;
        }
        this._fireCallback();
        this._counter++;
        if (this._counter >= this._list.length) {
            this._counter = 0;
            if (this._pauseOnComplete)
                this._looping = this._pauseOnComplete = false;
        }
        if (this._looping) setTimeout(this.method('stepForward'), this._interval);
        return this;
    },
    
    /**
     * <p>Makes the sequence step forward indefinately at timed intervals.</p>
     * @param {Number} time
     * @returns {Sequence}
     */
    loop: function(time) {
        this._interval = 1000 * Number(time || 0) || this._interval;
        if (!this._interval || this._looping) return this;
        this._looping = true;
        return this.stepForward();
    },
    
    /**
     * <p>Stops the sequence looping. The needle will be placed after the last called-back needle.</p>
     * @returns {Sequence}
     */
    pause: function() {
        if (this._looping) this._looping = null;
        return this;
    },
    
    /**
     * <p>Causes the sequence to stop looping when it reaches the end of the list.</p>
     * @returns {Sequence}
     */
    finish: function() {
        if (this._looping) this._pauseOnComplete = true;
        return this;
    }
});

/**
 * <p>Returns a <tt>Sequence</tt> object that cycles over every member of the array over
 * the given <tt>time</tt> interval. Your <tt>callback</tt> function is called every <tt>time</tt>
 * seconds, being passed each member of the array in turn and its position in the list.</p>
 *
 * <pre><code>    // Cycle over a set of images
 *     var imgs = ['/imgs/one.png', 'imgs/two.png', 'imgs/three.png'];
 *     var element = Ojay('#something');
 *     
 *     var sequence = imgs.sequence(function(imgageSource, i) {
 *         element.setAttributes({src: imageSource});
 *     });
 *     
 *     // Start sequence looping with a time period
 *     sequence.loop(5);
 *     
 *     // Pause the sequence
 *     sequence.pause();
 *     
 *     // Start again where we left off
 *     sequence.loop();
 *     
 *     // Stop when it next gets to the end of the list
 *     sequence.finish();</code></pre>
 *
 * @param {Number} time
 * @param {Function} callback
 * @returns {Sequence}
 */
Array.prototype.sequence = function(callback) {
    return new Ojay.Sequence(this, callback);
};

Ojay.DomCollection.include(/** @scope Ojay.DomCollection.prototype */{
    /**
     * <p>Returns a <tt>Sequence</tt> operating on the members of the collection.
     * See <tt>Array#sequence</tt> for more information.</p>
     * @param {Number} time
     * @param {Function} callback
     * @returns {Sequence}
     */
    sequence: function(callback) {
        return [].map.call(this, function(el) { return Ojay(el); })
                .sequence(callback);
    }
});

JS.MethodChain.addMethods(Ojay);
JS.MethodChain.addMethods(Ojay.HTML);

// Modify MethodChain to allow CSS selectors
JS.MethodChain.prototype._ = JS.MethodChain.prototype._.wrap(function() {
    var args = Array.from(arguments), _ = args.shift();
    if (typeof args[0] == 'string') return _(Ojay, args[0]);
    else return _.apply(this, args);
});

Ojay.VERSION = '0.2.0';
