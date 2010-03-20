/*
Copyright (c) 2007-2008 James Coglan, http://jsclass.jcoglan.com
Licensed under the MIT license, http://www.opensource.org/licenses/mit-license.php
*/
/**
 * Copyright (c) 2007-2008 James Coglan
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
 *
 * Parts of this software are derived from the following open-source projects:
 *
 * - The Prototype framework, (c) 2005-2007 Sam Stephenson
 * - Alex Arnell's Inheritance library, (c) 2006, Alex Arnell
 * - Base, (c) 2006-7, Dean Edwards
 */

JS = {
  extend: function(object, methods) {
    for (var prop in methods) object[prop] = methods[prop];
  },
  
  method: function(name) {
    var self = this, cache = self._methods = self._methods || {};
    if ((cache[name] || {}).fn == self[name]) return cache[name].bd;
    return (cache[name] = {fn: self[name], bd: self[name].bind(self)}).bd;
  },
  
  util: {}
};

Array.from = function(iterable) {
  if (!iterable) return [];
  if (iterable.toArray) return iterable.toArray();
  var length = iterable.length, results = [];
  while (length--) results[length] = iterable[length];
  return results;
};

JS.extend(Function.prototype, {
  bind: function() {
    var __method = this, args = Array.from(arguments), object = args.shift() || null;
    return function() {
      return __method.apply(object, args.concat(Array.from(arguments)));
    };
  },
  callsSuper: function() {
    return /\bcallSuper\b/.test(this.toString());
  },
  is: function(object) {
    return typeof object == 'function';
  }
});

JS.Class = function() {
  var args = Array.from(arguments), arg,
      parent = Function.is(args[0]) ? args.shift() : null,
      klass = JS.Class.create(parent);
  
  while (arg = args.shift())
    klass.include(arg);
  
  parent && Function.is(parent.inherited) &&
    parent.inherited(klass);
  
  return klass;
};

JS.extend(JS.Class, {
  create: function(parent) {
    var klass = function() {
      this.initialize.apply(this, arguments);
    };
    this.ify(klass);
    parent && this.subclass(parent, klass);
    var p = klass.prototype;
    p.klass = p.constructor = klass;
    klass.include(this.INSTANCE_METHODS, false);
    klass.instanceMethod('extend', this.INSTANCE_METHODS.extend, false);
    return klass;
  },
  
  ify: function(klass, noExtend) {
    klass.superclass = klass.superclass || Object;
    klass.subclasses = klass.subclasses || [];
    if (noExtend === false) return klass;
    for (var method in this.CLASS_METHODS)
      this.CLASS_METHODS.hasOwnProperty(method) &&
        (klass[method] = this.CLASS_METHODS[method]);
    return klass;
  },
  
  subclass: function(superklass, klass) {
    this.ify(superklass, false);
    klass.superclass = superklass;
    superklass.subclasses.push(klass);
    var bridge = function() {};
    bridge.prototype = superklass.prototype;
    klass.prototype = new bridge();
    klass.extend(superklass);
    return klass;
  },
  
  properties: function(klass) {
    var properties = {}, prop, K = this.ify(function(){});
    loop: for (var method in klass) {
      for (prop in K) { if (method == prop) continue loop; }
      properties[method] = klass[method];
    }
    return properties;
  },
  
  addMethod: function(object, superObject, name, func) {
    if (!Function.is(func)) return (object[name] = func);
    if (!func.callsSuper()) return (object[name] = func);
    
    var method = function() {
      var _super = superObject[name], args = Array.from(arguments), currentSuper = this.callSuper, result;
      Function.is(_super) && (this.callSuper = function() {
        var i = arguments.length;
        while (i--) args[i] = arguments[i];
        return _super.apply(this, args);
      });
      result = func.apply(this, arguments);
      currentSuper ? this.callSuper = currentSuper : delete this.callSuper;
      return result;
    };
    method.valueOf = function() { return func; };
    method.toString = function() { return func.toString(); };
    object[name] = method;
  },
  
  INSTANCE_METHODS: {
    initialize: function() {},
    
    method: JS.method,
    
    extend: function(source) {
      for (var method in source)
        source.hasOwnProperty(method) &&
          JS.Class.addMethod(this, this.klass.prototype, method, source[method]);
      return this;
    },
    
    isA: function(klass) {
      var _class = this.klass;
      while (_class) {
        if (_class === klass) return true;
        _class = _class.superclass;
      }
      return false;
    }
  },
  
  CLASS_METHODS: {
    include: function(source, overwrite) {
      var modules, i, n, inc = source.include, ext = source.extend;
      if (inc) {
        modules = [].concat(inc);
        for (i = 0, n = modules.length; i < n; i++)
          this.include(modules[i], overwrite);
      }
      if (ext) {
        modules = [].concat(ext);
        for (i = 0, n = modules.length; i < n; i++)
          this.extend(modules[i], overwrite);
      }
      for (var method in source) {
        !/^(included?|extend(ed)?)$/.test(method) &&
          this.instanceMethod(method, source[method], overwrite);
      }
      Function.is(source.included) && source.included(this);
      return this;
    },
    
    instanceMethod: function(name, func, overwrite) {
      if (!this.prototype[name] || overwrite !== false)
        JS.Class.addMethod(this.prototype, this.superclass.prototype, name, func);
      return this;
    },
    
    extend: function(source, overwrite) {
      Function.is(source) && (source = JS.Class.properties(source));
      for (var method in source) {
        source.hasOwnProperty(method) && !/^(included?|extend(ed)?)$/.test(method) &&
          this.classMethod(method, source[method], overwrite);
      }
      Function.is(source.extended) && source.extended(this);
      return this;
    },
    
    classMethod: function(name, func, overwrite) {
      for (var i = 0, n = this.subclasses.length; i < n; i++)
        this.subclasses[i].classMethod(name, func, false);
      (!this[name] || overwrite !== false) &&
        JS.Class.addMethod(this, this.superclass, name, func);
      return this;
    },
    
    method: JS.method
  }
});

JS.extend(JS, {
  Interface: JS.Class({
    initialize: function(methods) {
      this.test = function(object, returnName) {
        var n = methods.length;
        while (n--) {
          if (!Function.is(object[methods[n]]))
            return returnName ? methods[n] : false;
        }
        return true;
      };
    },
    
    extend: {
      ensure: function() {
        var args = Array.from(arguments), object = args.shift(), face, result;
        while (face = args.shift()) {
          result = face.test(object, true);
          if (result !== true) throw new Error('object does not implement ' + result + '()');
        }
      }
    }
  }),
  
  Singleton: function() {
    return new (JS.Class.apply(JS, arguments));
  },
  
  Module: function(source) {
    return {
      included: function(klass) { klass.include(source); },
      extended: function(klass) { klass.extend(source); }
    };
  }
});

JS.MethodChain = function(base) {
  var queue = [], baseObject = base || {};
  
  this.____ = function(method, args) {
    queue.push({func: method, args: args});
  };
  
  this.fire = function(base) {
    return JS.MethodChain.fire(queue, base || baseObject);
  };
};

JS.MethodChain.fire = function(queue, object) {
  var method, property, i, n;
  loop: for (i = 0, n = queue.length; i < n; i++) {
    method = queue[i];
    if (object instanceof JS.MethodChain) {
      object.____(method.func, method.args);
      continue;
    }
    switch (typeof method.func) {
      case 'string':    property = object[method.func];       break;
      case 'function':  property = method.func;               break;
      case 'object':    object = method.func; continue loop;  break;
    }
    object = (typeof property == 'function')
        ? property.apply(object, method.args)
        : property;
  }
  return object;
};

JS.MethodChain.prototype = {
  _: function() {
    var base = arguments[0], args, i, n;
    switch (typeof base) {
      case 'object': case 'function':
        args = [];
        for (i = 1, n = arguments.length; i < n; i++) args.push(arguments[i]);
        this.____(base, args);
    }
    return this;
  },
  
  toFunction: function() {
    var chain = this;
    return function(object) { return chain.fire(object); };
  }
};

JS.MethodChain.reserved = (function() {
  var names = [], key;
  for (key in new JS.MethodChain) names.push(key);
  return new RegExp('^(?:' + names.join('|') + ')$');
})();

JS.MethodChain.addMethod = function(name) {
  if (this.reserved.test(name)) return;
  this.prototype[name] = function() {
    this.____(name, arguments);
    return this;
  };
};

JS.MethodChain.addMethods = function(object) {
  var methods = [], property, i, n;
  
  for (property in object)
    Number(property) != property && methods.push(property);
  
  if (object instanceof Array) {
    for (i = 0, n = object.length; i < n; i++)
      typeof object[i] == 'string' && methods.push(object[i]);
  }
  for (i = 0, n = methods.length; i < n; i++)
    this.addMethod(methods[i]);
  
  object.prototype &&
    this.addMethods(object.prototype);
};

it = its = function() { return new JS.MethodChain; };

JS.Class.addMethod = (function(wrapped) {
  return function() {
    JS.MethodChain.addMethods([arguments[2]]);
    return wrapped.apply(JS.Class, arguments);
  };
})(JS.Class.addMethod);

(function(methods) {
  JS.extend(JS.Class.INSTANCE_METHODS, methods);
  JS.extend(JS.Class.CLASS_METHODS, methods);
})({
  wait: function(time) {
    var chain = new JS.MethodChain;
    
    typeof time == 'number' &&
      setTimeout(chain.fire.bind(chain, this), time * 1000);
    
    this.forEach && typeof time == 'function' &&
      this.forEach(function() {
        setTimeout(chain.fire.bind(chain, arguments[0]), time.apply(this, arguments) * 1000);
      });
    
    return chain;
  },
  
  _: function() {
    var base = arguments[0], args = [], i, n;
    for (i = 1, n = arguments.length; i < n; i++) args.push(arguments[i]);
    return  (typeof base == 'object' && base) ||
            (typeof base == 'function' && base.apply(this, args)) ||
            this;
  }
});

JS.Observable = {
  addObserver: function(observer, context) {
    (this._observers = this._observers || []).push({bk: observer, cx: context || null});
  },
  
  removeObserver: function(observer, context) {
    this._observers = this._observers || [];
    context = context || null;
    for (var i = 0, n = this.countObservers(); i < n; i++) {
      if (this._observers[i].bk == observer && this._observers[i].cx == context) {
        this._observers.splice(i,1);
        return;
      }
    }
  },
  
  removeObservers: function() {
    this._observers = [];
  },
  
  countObservers: function() {
    return (this._observers = this._observers || []).length;
  },
  
  notifyObservers: function() {
    if (!this.isChanged()) return;
    for (var i = 0, n = this.countObservers(), observer; i < n; i++) {
      observer = this._observers[i];
      observer.bk.apply(observer.cx, arguments);
    }
  },
  
  setChanged: function(state) {
    this._changed = !(state === false);
  },
  
  isChanged: function() {
    if (this._changed === undefined) this._changed = true;
    return !!this._changed;
  }
};

JS.Observable.subscribe   = JS.Observable.addObserver;
JS.Observable.unsubscribe = JS.Observable.removeObserver;
JS.Observable = JS.Module(JS.Observable);

JS.State = JS.Module({
  _getState: function(state) {
    return  (typeof state == 'object' && state) ||
            (typeof state == 'string' && ((this.states || {})[state] || {})) ||
            {};
  },
  
  setState: function(state) {
    this._state = this._getState(state);
    JS.util.State.addMethods(this._state, this.klass);
  },
  
  inState: function() {
    for (var i = 0, n = arguments.length; i < n; i++) {
      if (this._state == this._getState(arguments[i])) return true;
    }
    return false;
  }
});

JS.util.State = {
  stub: function() { return this; },
  
  buildStubs: function(stubs, collection, states) {
    var state, method;
    for (state in states) {
      collection[state] = {};
      for (method in states[state]) stubs[method] = this.stub;
  } },
  
  buildCollection: function(addMethod, proto, superproto, states) {
    var stubs = {}, collection = {}, superstates = superproto.states || {};
    this.buildStubs(stubs, collection, states);
    this.buildStubs(stubs, collection, superstates);
    var state, klass;
    for (state in collection) {
      klass = (superstates[state]||{}).klass;
      klass = klass ? JS.Class(klass, states[state]) : JS.Class(states[state]);
      klass.include(stubs, false);
      collection[state] = new klass;
      JS.util.State.addMethods(collection[state], proto.klass);
    }
    return addMethod.call(JS.Class, proto, superproto, 'states', collection);
  },
  
  addMethods: function(state, klass) {
    for (var method in state) this.addMethod(klass, method);
  },
  
  addMethod: function(klass, method) {
    klass.instanceMethod(method, function() {
      var func = (this._state || {})[method];
      return func ? func.apply(this, arguments): this;
    }, false);
  }
};

JS.Class.addMethod = (function(wrapped) {
  return function(object, superObject, name, block) {
    if (name != 'states' || typeof block != 'object') return wrapped.apply(JS.Class, arguments);
    return JS.util.State.buildCollection(wrapped, object, superObject, block);
  };
})(JS.Class.addMethod);
