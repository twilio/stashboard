/*
Copyright (c) 2007-2008 the OTHER media Limited
Licensed under the BSD license, http://ojay.othermedia.org/license.html
*/
// @require ojay/core-min
(function(KeyListener, Event, doc) {
    var KEYS = KeyListener.KEY;

var /**
     * @param {String} string
     * @returns {Array}
     */
    w = function(string) {
        string = string.trim();
        return string ? string.split(/\s+/) : [];
    },
    
    /**
     * @param {Number} a
     * @param {Number} b
     * @returns {Number}
     */
    compareNumbers = function(a, b) {
        return a - b;
    },
    
    /**
     * @param {String} key
     * @returns {Number}
     */
    codeFor = function(key) {
        return key && String(key).toUpperCase().charCodeAt(0);
    },
    
    /**
     * @param {String|Array} keylist
     * @returns {Array}
     */
    codesFromKeys = function(keylist) {
        if (typeof keylist == 'string') keylist = w(keylist);
        return keylist.map(function(key) {
            var value = null;
            if (value = KEYS[String(key).toUpperCase()]) key = value;
            if (typeof key == 'string') key = codeFor(key);
            return key;
        }).sort(compareNumbers);
    },
    
    /**
     * @param {Array} codes
     * @returns {Object}
     */
    hashFromCodes = function(codes) {
        return codes.reduce(function(hash, code) {
            switch (code) {
                case KEYS.CONTROL:  hash.ctrl = true;   break;
                case KEYS.SHIFT:    hash.shift = true;  break;
                case KEYS.ALT:      hash.alt = true;    break;
                default:
                    hash.keys.push(code);
            }
            return hash;
        }, {keys: []});
    },
    
    /**
     * @param {Array} codes
     * @returns {String}
     */
    signature = function(codes) {
        return codes.sort(compareNumbers).join(':');
    };

/**
 * <p>The <tt>Keyboard</tt> package is used to set up event listeners that respond to keyboard
 * events. It acts as a wrapper around <tt>YAHOO.util.KeyListener</tt> and provides easier syntax
 * and more control of sets of keyboard rules. To set up a keyboard listener, call:</p>
 *
 * <pre><code>    Ojay.Keyboard.listen(document, 'SHIFT B', function() { ... });</code></pre>
 *
 * <p>This returns a <tt>Rule</tt> instance that lets you disable/enable the listener. See the
 * <tt>Rule</tt> class for more details.</p>
 */
var Keyboard = Ojay.Keyboard = new JS.Singleton({
    
    /**
     * <p>Returns a new <tt>Rule</tt> instance for the given node and key combination.</p>
     * @param {HTMLElement|String} node
     * @param {String} keys
     * @param {Function} callback
     * @param {Object} scope
     * @returns {Rule}
     */
    listen: function(node, keys, callback, scope) {
        var rule = new Rule(node, keys, callback, scope);
        rule.enable();
        return rule;
    },
    
    /**
     * <p>Returns <tt>true</tt> iff the given key combination is currently pressed.</p>
     * @param {String} keys
     * @returns {Boolean}
     */
    isPressed: function(keys) {
        return codesFromKeys(keys).every(Monitor.method('_isPressed'));
    }
});

/**
 * <p> The <tt>Rule</tt> class encapsulates the binding of an action to a set of keys. It is
 * private, i.e. it is only accessible to the internals of the <tt>Keyboard</tt> module, but
 * instances of it may be returned by the <tt>Keyboard</tt> interface.</p>
 * @constructor
 * @private
 * @class Rule
 */
var Rule = new JS.Class({
    /**
     * @param {HTMLElement} node
     * @param {String|Array} keylist
     * @param {Function} callback
     * @param {Object} scope
     */
    initialize: function(node, keylist, callback, scope) {
        node = Ojay(node).node;
        if (scope) callback = callback.bind(scope);
        this._codes = codesFromKeys(keylist);
        this._listener = new KeyListener(node, hashFromCodes(this._codes), callback);
    },
    
    /**
     * <p>Makes the rule active.</p>
     * @returns {Rule}
     */
    enable: function() {
        this._active = true;
        this._listener.enable();
        this._prevents_default && Disabler._register(this);
        return this;
    },
    
    /**
     * <p>Makes the rule inactive.</p>
     * @returns {Rule}
     */
    disable: function() {
        this._active = false;
        this._listener.disable();
        this._prevents_default && Disabler._unregister(this);
        return this;
    },
    
    /**
     * <p>Causes the rule to prevent the browser's default behaviour.</p>
     * @returns {Rule}
     */
    preventDefault: function() {
        this._prevents_default = true;
        this._active && Disabler._register(this);
        return this;
    },
    
    /**
     * <p>Causes the rule to allow the browser's default behaviour.</p>
     * @returns {Rule}
     */
    allowDefault: function() {
        this._prevents_default = false;
        this._active && Disabler._unregister(this);
        return this;
    },
    
    /**
     * <p>Returns a string that represents the set of key codes the rule applies to.</p>
     * @returns {String}
     */
    getSignature: function() {
        var sig = signature(this._codes);
        this.getSignature = function() { return sig; };
        return sig;
    }
});

/**
 * <p>The <tt>RuleSet</tt> class is used to set up contexts in which key combinations are mapped
 * to actions. These contexts can be activated and deactivated easily to modify the behaviour of
 * the keyboard. This class is publicly accessible. An example:</p>
 *
 * <pre><code>    var rules = new Ojay.Keyboard.RuleSet({
 *         'UP':            function() { console.log('up'); },
 *         'CONTROL DOWN':  function() { console.log('down'); },
 *         'ALT SHIFT K':   function() { console.log('weird') }
 *     });</code></pre>
 *
 * @constructor
 * @public
 * @class RuleSet
 */
Keyboard.RuleSet = new JS.Class({
    /**
     * @param {Object} definitions
     */
    initialize: function(definitions) {
        this._rules = {};
        var keylist, rule;
        for (keylist in definitions) {
            rule = new Rule(document, keylist, definitions[keylist]);
            // Store rules by signature to prevent duplicate key combinations
            this._rules[rule.getSignature()] = rule;
        }
    },
    
    /**
     * <p>Calls the given function with each rule in the set in turn.</p>
     * @param {Function} block
     * @param {Object} context
     */
    forEach: function(block, context) {
        block = Function.from(block);
        for (var signature in this._rules)
            block.call(context || null, this._rules[signature]);
    },
    
    /**
     * <p>Enables the set of rules.</p>
     * @returns {Keyboard.RuleSet}
     */
    enable: function() {
        this.forEach('enable');
        return this;
    },
    
    /**
     * <p>Disables the set of rules.</p>
     * @returns {Keyboard.RuleSet}
     */
    disable: function() {
        this.forEach('disable');
        return this;
    },
    
    /**
     * @param {String} keys
     * @returns {Rule}
     */
    get: function(keys) {
        return this._rules[signature(codesFromKeys(keys))] || null;
    },
    
    /**
     * @param {RuleSet} ruleSet
     * @returns {RuleSet}
     */
    merge: function(ruleSet) {
        var rules = {},
            addRule = function(rule) { rules[rule.getSignature()] = rule; };
        
        [this, ruleSet].forEach({forEach: addRule});
        var set = new this.klass({});
        set._rules = rules;
        return set;
    }
});

/**
 * <p>The <tt>Monitor</tt> is a private component used by the Keyboard package to track
 * the current combination of pressed keys. Event handlers notify this object with keys
 * to add and remove from the list. This object may be consulted to find out whether
 * a particular key code is pressed.</p>
 */
var Monitor = new JS.Singleton({
    _list: [],
    
    /**
     * <p>Adds a key code to the list.</p>
     * @param {Number} key
     */
    _addKey: function(key) {
        if (!this._isPressed(key)) this._list.push(key);
    },
    
    /**
     * <p>Removes a key code from the list.</p>
     * @param {Number} key
     */
    _removeKey: function(key) {
        this._list = this._list.filter(function(x) { return x != key; });
    },
    
    /**
     * <p>Returns <tt>true</tt> iff the given key code is currently pressed.</p>
     * @param {Number} key
     * @returns {Boolean}
     */
    _isPressed: function(key) {
        return this._list.indexOf(key) != -1;
    },
    
    /**
     * <p>Returns a string uniquely identifying the current set of pressed keys.</p>
     * @returns {String}
     */
    getSignature: function() {
        return signature(this._list);
    }
});

/**
 * <p>The <tt>Disabler</tt> is in charge of deciding whether to prevent the default browser
 * behaviour for a given set of keys. Keyboard rules register with this object to cause
 * their behaviour to override the default behaviour. Some browsers do not allow certain
 * key comibnations to be overridden, so choose your key combinations carefully.</p>
 */
var Disabler = new JS.Singleton({
    _rules: [],
    
    /**
     * <p>Adds a <tt>Rule</tt> to the list.</p>
     * @param {Rule} rule
     */
    _register: function(rule) {
        this._rules.push(rule);
    },
    
    /**
     * <p>Removes a <tt>Rule</tt> from the list.</p>
     * @param {Rule} rule
     */
    _unregister: function(rule) {
        this._rules = this._rules.filter(function(x) { return x != rule; });
    },
    
    /**
     * <p>Given an event and the current key signature, decides whether to prevent the
     * default reaction to the event.</p>
     * @param {Event} evnt
     * @param {String} signature
     */
    _processEvent: function(evnt, signature) {
        if (this._recognizesSignature(signature))
            Event.preventDefault(evnt);
    },
    
    /**
     * <p>Returns <tt>true</tt> iff the current list of rules contains any rule whose
     * key combination matches the given signature.</p>
     * @param {String} signature
     * @returns {Boolean}
     */
    _recognizesSignature: function(signature) {
        for (var i = 0, n = this._rules.length; i < n; i++) {
            if (this._rules[i].getSignature() == signature)
                return true;
        }
        return false;
    }
});

/**
 * <p>On keydown events, add the new key to the <tt>Monitor</tt> and decide whether
 * to stop the event in IE browsers.</p>
 */
Event.on(doc, 'keydown', function(evnt) {
    Monitor._addKey(evnt.keyCode);
    if (YAHOO.env.ua.ie)
        Disabler._processEvent(evnt, Monitor.getSignature());
});

/**
 * <p>On keypress events, decide whether to stop the event in non-IE browsers.</p>
 */
if (!YAHOO.env.ua.ie) {
    Event.on(doc, 'keypress', function(evnt) {
        Disabler._processEvent(evnt, Monitor.getSignature());
    });
}

/**
 * <p>On keyup events, remove the key from the <tt>Monitor</tt>.</p>
 */
Event.on(doc, 'keyup', function(evnt) {
    Monitor._removeKey(evnt.keyCode);
});

})(YAHOO.util.KeyListener, YAHOO.util.Event, document);
