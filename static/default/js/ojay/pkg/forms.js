/*
Copyright (c) 2007-2008 the OTHER media Limited
Licensed under the BSD license, http://ojay.othermedia.org/license.html
*/
// @require ojay/core-min
// @require ojay/pkg/http-min
(function() {

JS.extend(Ojay, /** @scope Ojay */ {
    /**
     * <p>Returns <tt>true</tt> iff the given value is truthy and is not just whitespace.</p>
     * @param {String} value
     * @returns {Boolean}
     */
    isBlank: function(value) {
        return value ? false : (String(value).trim() == '');
    },
    
    /**
     * <p>Returns <tt>true</tt> iff the given <tt>value</tt> is a number.</p>
     * @param {String} value
     * @returns {Boolean}
     */
    isNumeric: function(value) {
        return this.NUMBER_FORMAT.test(String(value));
    },
    
    /**
     * <p>Returns <tt>true</tt> iff the given <tt>value</tt> is an email address.</p>
     * @param {String} value
     * @returns {Boolean}
     */
    isEmailAddress: function(value) {
        return this.EMAIL_FORMAT.test(String(value));
    },
    
    /**
     * <p>JSON number definition from http://json.org</p>
     */
    NUMBER_FORMAT: /^\-?(0|[1-9]\d*)(\.\d+)?(e[\+\-]?\d+)?$/i,
    
    /**
     * <p>Format for valid email addresses from http://www.regular-expressions.info/email.html</p>
     */
    EMAIL_FORMAT: /^[a-z0-9!#$%&'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+\/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+(?:[A-Z]{2}|com|org|net|gov|mil|biz|info|mobi|name|aero|jobs|museum)\b$/i
});

Ojay.Forms = function(description) {
    description.call(DSL);
};

// Stores all instances of styled form controls.
var styledInputs = [];

JS.extend(Ojay.Forms, /** @scope Ojay.Forms */{
    /**
     * <p>Returns an Ojay collection wrapping the label for the given input.</p>
     * @param {String|HTMLElement|DomCollection} input
     * @returns {DomCollection}
     */
    getLabel: function(input) {
        input = Ojay(input);
        if (!input.node) return Ojay();
        var label = input.ancestors('label');
        if (label.node) return label.at(0);
        var id = input.node.id;
        label = [].filter.call(document.getElementsByTagName('label'), function(label) { return id && label.htmlFor == id; });
        return Ojay(label.slice(0,1));
    },
    
    /**
     * <p>Returns the serialization of the given <tt>form</tt> as a string.</p>
     * @param {String|HTMLElement|DomCollection} form
     * @returns {String}
     */
    getQueryString: function(form) {
        var data = YAHOO.util.Connect.setForm(Ojay(form).node);
        YAHOO.util.Connect.resetFormState();
        return data;
    },
    
    /**
     * <p>Returns the serialization of the given <tt>form</tt> as an object.</p>
     * @param {String|HTMLElement|DomCollection} form
     * @returns {Object}
     */
    getData: function(form) {
        return this.getQueryString(form).split('&').reduce(function(memo, pair) {
            var data = pair.split('=').map(decodeURIComponent).map('trim');
            if (memo[data[0]] === undefined) memo[data[0]] = data[1];
            return memo;
        }, {});
    },
    
    /**
     * @param {String|HTMLElement|DomCollection}
     * @param {String|Boolean} value
     */
    setValue: function(element, value) {
        var selected, options, element = Ojay(element);
        switch (true) {
            
            case element.every({matches: '[type=radio]'}) :
                selected = element.map('node').filter({value: value})[0];
                if (!selected) return;
                element.setAttributes({checked: false});
                selected.checked = true;
                break;
            
            case element.matches('[type=checkbox]') :
                element.node.checked = !!(value === true || value == element.node.value);
                break;
            
            case element.matches('select') :
                options = Array.from(element.node.options);
                selected = options.filter({value: value})[0];
                if (!selected) return;
                options.forEach(function(option) { option.selected = false });
                selected.selected = true;
                break;
            
            case element.matches('input') :
            case element.matches('[type=hidden]') :
            case element.matches('textarea') :
                element.node.value = String(value);
                break;
        }
    }.curry(),
    
    /**
     * <p>Goes through all sets of form rules and makes sure each one is associated with
     * an existing form in the document. Useful for replacing a form dynamically and then
     * reattaching all the rules. Returns the number of reattached forms.</p>
     * @returns {Number}
     */
    reattach: function() {
        var n = 0;
        for (var id in forms) {
            if (forms[id]._attach()) ++n;
        }
        return n;
    },
    
    /**
     * <p>Makes sure all styled form inputs are displaying the right values from the
     * underlying form inputs.</p>
     */
    update: function() {
        styledInputs.forEach(function(input) {
            if (input.isA(Ojay.Forms.Select)) input._updateDisplayFromSelect();
            else input.setChecked();
        });
    }
});

/**
 * <p>The <tt>FormDescription</tt> class encapsulates sets of rules about how a form is to
 * behave. Each instance holds a set of requirements, which are tested against the form's
 * data each time the form is submitted in order to decide whether to allow submission to
 * the server.</p>
 * @constructor
 * @class FormDescription
 * @private
 */
var FormDescription = new JS.Class(/** @scope FormDescription.prototype */{
    include: JS.Observable,
    
    /**
     * @param {String} id
     */
    initialize: function(id) {
        this._formID = id;
        this._displayNames = {};
        this._attach();
        
        this._requirements   = {};
        this._validators     = [];
        this._dataFilters    = [];
        this._ajaxResponders = [];
        this._dsl    = new FormDSL(this);
        this._when   = new WhenDSL(this);
        this._before = new BeforeDSL(this);
    },
    
    /**
     * <p>Finds the form element in the document and hijacks its submit event. Returns a
     * boolean to indicate whether the form was reattached.</p>
     * @returns {Boolean}
     */
    _attach: function() {
        if (this._hasForm()) return false;
        this._inputs = {};
        this._labels = {};
        this._names  = {};
        this._form = Ojay.byId(this._formID);
        if (!this._hasForm()) return false;
        this._form.on('submit', this.method('_handleSubmission'));
        for (var field in this._requirements) this._requirements[field]._attach();
        return true;
    },
    
    /**
     * <p>Returns <tt>true</tt> iff the description object has an associated <tt>form</tt>
     * element in the current document.</p>
     * @returns {Boolean}
     */
    _hasForm: function() {
        return this._form && this._form.matches('body form');
    },
    
    /**
     * <p>Returns the <tt>FormRequirement</tt> object for the named field. If no existing
     * requirement object is found for the field, a new one is created for it.</p>
     * @param {String} name
     * @returns {FormRequirement}
     */
    _getRequirement: function(name) {
        return this._requirements[name] || (this._requirements[name] = new FormRequirement(this, name));
    },
    
    /**
     * <p>Processes form submission events by validating the form and stopping the event
     * from proceeding if the form data is found to be invalid.</p>
     * @param {DomCollection} form
     * @param {Event} evnt
     */
    _handleSubmission: function(form, evnt) {
        var valid = this._isValid();
        if (this._ajax || !valid) evnt.stopDefault();
        if (!this._ajax || !valid) return;
        var form = this._form.node;
        Ojay.HTTP[(form.method || 'POST').toUpperCase()](form.action, this._data, {
            onSuccess: function(response) {
                this._ajaxResponders.forEach({call: [null, response]});
            }.bind(this)
        });
    },
    
    /**
     * <p>Returns an Ojay collection representing all the inputs in the form with the given
     * <tt>name</tt>.</p>
     * @param {String} name
     * @return {DomCollection}
     */
    _getInputs: function(name) {
        if (this._inputs[name]) return this._inputs[name];
        var inputs = this._form.descendants('input, textarea, select');
        if (name) inputs = inputs.filter(function(element) { return element.node.name == name; });
        return this._inputs[name] = inputs;
    },
    
    /**
     * <p>Returns an Ojay collection for the <tt>label</tt> tag for a specified <tt>name</tt>
     * or element referece.</p>
     * @param {String|HTMLElement|DomCollection} name
     * @returns {DomCollection}
     */
    _getLabel: function(name) {
        if (name.node) name = name.node;
        if (name.name) name = name.name;
        return this._labels[name] || ( this._labels[name] = Ojay.Forms.getLabel(this._getInputs(name)) );
    },
    
    /**
     * <p>Returns a human-readable name for the given field. If the developer has not specified
     * a name, it is inferred from the field's label, or from the field's name itself if no label
     * is found.</p>
     * @param {String} name
     * @returns {String}
     */
    _getName: function(field) {
        if (this._names[field]) return this._names[field];
        if (this._displayNames[field]) return this._names[field] = this._displayNames[field];
        var label = this._getLabel(field);
        var name = ((label.node || {}).innerHTML || field).stripTags();
        
        name = name.replace(/(\w)[_-](\w)/g, '$1 $2')
                .replace(/([a-z])([A-Z])/g, function(match, a, b) {
                    return a + ' ' + b.toLowerCase();
                });
        
        return this._names[field] = name.charAt(0).toUpperCase() + name.substring(1);
    },
    
    /**
     * <p>Returns the data in the form using <tt>YAHOO.util.Connect</tt>.</p>
     * @returns {Object}
     */
    _getData: function() {
        return this._data = Ojay.Forms.getData(this._form);
    },
    
    /**
     * <p>Validates the form by applying the set of requirements to the form's current data and
     * building up a collection of errors, and notifies any observers that validation has taken
     * place.</p>
     */
    _validate: function() {
        this._errors = new FormErrors(this);
        var data = this._getData(), key, input;
        
        this._dataFilters.forEach(function(filter) { filter(data); });
        for (key in data) Ojay.Forms.setValue(this._getInputs(key), data[key]);
        Ojay.Forms.update();
        
        data = new FormData(data);
        for (key in this._requirements)
            this._requirements[key]._test(data.get(key), data);
        
        this._validators.forEach(function(validate) { validate(data, this._errors); }, this);
        
        var fields = this._errors._fields();
        for (key in this._inputs)
            [this._getInputs(key), this._getLabel(key)].forEach(
                it()[fields.indexOf(key) == -1 ? 'removeClass' : 'addClass']('invalid'));
        
        this.notifyObservers(this);
    },
    
    /**
     * <p>Returns <tt>true</tt> iff the form's current data is valid according to the set
     * of stored requirements.</p>
     * @returns {Boolean}
     */
    _isValid: function() {
        this._validate();
        return this._errors._count() === 0;
    },
    
    /**
     * <p>Causes the form's inputs and labels to add/remove the class name 'focused' in response
     * to user interaction, to allow you to highlight the active field with CSS.</p>
     */
    _highlightActiveField: function() {
        this._getInputs('').forEach(function(input) {
            input.on('focus').addClass('focused')._(this)._getLabel(input).addClass('focused');
            input.on('blur').removeClass('focused')._(this)._getLabel(input).removeClass('focused');
        }, this);
    }
});

var isPresent = function(value) {
    return !Ojay.isBlank(value) || ['must not be blank'];
};

/**
 * <p>The <tt>FormRequirement</tt> class encapsulates a set of tests against the value of a single
 * form field. The tests are defined externally and added using the <tt>_add()</tt> method. Each
 * test should be a function that takes a value and decides whether or not it is valid. The
 * <tt>FormRequirement</tt> instance can be used to run all the tests against a field.</p>
 * @constructor
 * @class FormRequirement
 * @private
 */
var FormRequirement = new JS.Class({
    /**
     * @param {FormDescription} form
     * @param {String} field
     */
    initialize: function(form, field) {
        this._form = form;
        this._field = field;
        this._tests = [];
        this._dsl = new RequirementDSL(this);
        this._attach();
    },
    
    /**
     */
    _attach: function() {
        this._elements = this._form._getInputs(this._field);
    },
    
    /**
     * @param {Function} block
     */
    _add: function(block) {
        this._tests.push(block);
    },
    
    /**
     * @param {String} value
     * @param {Object} data
     * @returns {Array|Boolean}
     */
    _test: function(value, data) {
        var errors = [], tests = this._tests.length ? this._tests : [isPresent], value = value || '';
        tests.forEach(function(block) {
            var result = block(value, data), message, field;
            if (result !== true) {
                message = result[0]; field = result[1] || this._field;
                this._form._errors.register(this._field);
                this._form._errors.add(field, message);
            }
        }, this);
        return errors.length ? errors : true;
    }
});

/**
 * <p>The <tt>FormData</tt> class provides read-only access to data objects for the
 * purposes of validation. Validation routines cannot modify form data through this
 * class. To use it, pass an object to the constructor. The resulting instance will
 * provide a <tt>get()</tt> method to retrieve fields from the object but will not
 * let you write to these fields.</p>
 * @contructor
 * @class FormData
 * @private
 */
var FormData = new JS.Class(/** @scope FormData.prototype */{
    /**
     * @param {Object} data
     */
    initialize: function(data) {
        this.get = function(field) {
            return data[field] === undefined ? null : data[field];
        };
    }
});

/**
 * <p>The <tt>FormErrors</tt> class provides append-only access to error lists for the
 * purposes of validation. Validation routines cannot modify existing errors or remove
 * them from the list, so existing validation rules cannot be bypassed.</p>
 * @contructor
 * @class FormErrors
 * @private
 */
var FormErrors = new JS.Class(/** @scope FormErrors.prototype */{
    initialize: function(form) {
        var errors = {}, base = [];
        
        /**
         * <p>Creates storage space to put errors for the named field</p>
         * @param {String} field
         * @returns {FormErrors}
         */
        this.register = function(field) {
            errors[field] = errors[field] || [];
            return this;
        };
        
        /**
         * <p>Adds an error to the given <tt>field</tt> with message <tt>message</tt>.</p>
         * @param {String} field
         * @param {String} message
         * @returns {FormErrors}
         */
        this.add = function(field, message) {
            this.register(field);
            if (errors[field].indexOf(message) == -1) errors[field].push(message);
            return this;
        };
        
        /**
         * <p>Adds an error to the form as a whole rather than to an individual field.</p>
         * @param {String} message
         * @returns {FormErrors}
         */
        this.addToBase = function(message) {
            base.push(message);
            return this;
        };
        
        /**
         * <p>Returns the number of errors.</p>
         * @returns {Number}
         */
        this._count = function() {
            var n = base.length;
            for (var field in errors) n += errors[field].length;
            return n;
        };
        
        /**
         * <p>Returns an array of objects representing the errors in the form.<p>
         * @returns {Array}
         */
        this._messages = function() {
            var name, messages = base.map(function(message) {
                return {field: null, message: message};
            });
            for (var field in errors) {
                name = form._getName(field);
                errors[field].forEach(function(message) {
                    messages.push({field: field, message: name + ' ' + message});
                });
            }
            return messages;
        };
        
        /**
         * <p>Returns a list of field names that currently are invalid.</p>
         * @returns {Array}
         */
        this._fields = function() {
            var fields = [];
            for (var field in errors) fields.push(field);
            return fields;
        };
    }
});

/**
 * @overview
 *
 * <p><tt>Ojay.Forms</tt> provides a DSL-style API for writing specs for validating form input,
 * handling errors when they occur, and allowing forms to be submitted using Ajax. Its most basic
 * building block is the <tt>requires</tt> statement, which expresses the fact that a given field
 * must contain some data in order to be valid. You write all your form specs within a block like
 * the following:</p>
 *
 * <pre><code>    Ojay.Forms(function() { with(this) {
 *         
 *         // The form with id 'foo' requires field named 'bar'
 *         form('foo').requires('bar');
 *     }});</code></pre>
 *
 * <p>Note that, although all these examples have their own <tt>Ojay.Forms()</tt> block, you could
 * put them all in one block together.</p>
 *
 * <p>You can also use the word <tt>expects</tt> in place of <tt>requires</tt> -- the two perform
 * exactly the same function. As well as simply requiring a field, you can say what form the input
 * should take using a variety of pre-built validator functions. Here's an example:</p>
 *
 * <pre><code>    Ojay.Forms(function() { with(this) {
 *         
 *         form('theForm')
 *             .requires('username').toHaveLength({minimum: 6})
 *             .requires('email').toMatch(EMAIL_FORMAT)
 *             .expects('tickets').toBeNumeric();
 *     }});</code></pre>
 *
 * <p>The full list of validator methods can be found in the <tt>RequirementDSL</tt> class. All
 * requirments take as their last argument an optional string specifying the text that should
 * be displayed in the error message if the field is invalid. Additionally, the <tt>requires</tt>
 * and <tt>expects</tt> methods take an optional argument to specify how the name of the field
 * should be presented. If no custom name is given for the field, a name is inferred from the field's
 * label or its <tt>name</tt> attribute.</p>
 *
 * <pre><code>    Ojay.Forms(function() { with(this) {
 *         
 *         // Gives message "User email is not valid"
 *         form('signup').requires('userEmail').toMatch(EMAIL_FORMAT);
 *         
 *         // Gives message "Your email address is not valid"
 *         form('signup').requires('userEmail', 'Your email address').toMatch(EMAIL_FORMAT);
 *         
 *         // Gives message "User email is not a valid email address"
 *         form('signup').requires('userEmail').toMatch(EMAIL_FORMAT, 'is not a valid email address');
 *     }});</code></pre>
 *
 * <p>You can add your own custom validation routines using the <tt>validates</tt> method. In
 * your validation callback, you have access to the form's data and its error list. You can
 * read from the data and add errors as follows:</p>
 *
 * <pre><code>    Ojay.Forms(function() { with(this) {
 *         
 *         form('purchase').validates(function(data, errors) {
 *             
 *             // Check a field and add error to that field
 *             if (data.get('ccNumber').length != 16)
 *                 errors.add('ccNumber', 'is not a valid credit card number');
 *             
 *             // Check two fields and add error to the form
 *             // rather than to a specific field
 *             if (data.get('start') > data.get('end'))
 *                 errors.addToBase('Start date must be before end date');
 *         });
 *     }});</code></pre>
 *
 * <p>Once you've set up all your rules you'll want to do something with the errors. This
 * is where the helper function <tt>when</tt> comes in. <tt>when</tt> is used to set up
 * responses to events, and can handle validation events. In the example below, the callback
 * is passed an array of errors, each of which has a <tt>field</tt> property that says which
 * input name it belongs to (null if it was added using <tt>addToBase</tt>) and a
 * <tt>message</tt> field that contains the full text of the error message.</p>
 *
 * <pre><code>    Ojay.Forms(function() { with(this) {
 *         
 *         when('purchase').isValidated(function(errors) {
 *             errors.forEach(function(error) {
 *                 Ojay('#someElement').insert(error.message, 'top');
 *             });
 *         });
 *         
 *         // Ojay provides a pre-build error handler that lists the
 *         // errors in the element you specify:
 *         when('purchase').isValidated(displayErrorsIn('#error-list'));
 *     }});</code></pre>
 *
 * <p>Finally, the DSL allows you specify that a form submits using Ajax. To use this
 * feature, you just need to tell Ojay what to do with the server response. For example:</p>
 *
 * <pre><code>    Ojay.Forms(function() { with(this) {
 *         
 *         form('login').submitsUsingAjax();
 *         
 *         when('login').responseArrives(function(response) {
 *             Ojay('#response').setContent(response.responseText);
 *         });
 *         
 *         // Or use Ojay's pre-built display method:
 *         when('login').responseArrives(displayResponseIn('#response'));
 *     }});</code></pre>
 */

// Store to hold sets of form rules, entry per page form.
var forms = {};

/**
 * <p>Returns the <tt>FormDescription</tt> for the given <tt>id</tt>. A new description is
 * created if one does not already exist for the <tt>id</tt>.</p>
 * @param {String} id
 * @returns {FormDescription}
 * @private
 */
var getForm = function(id) {
    return forms[id] || (forms[id] = new FormDescription(id));
};

/**
 * <p>This is the main DSL object for <tt>Ojay.Forms</tt>. It contains methods that should
 * act as top-level functions in the DSL. Do not put a method in here unless it needs to be
 * a top-level function.</p>
 * @private
 */
var DSL = {
    /**
     * <p>Returns a DSL object for describing the form with the given <tt>id</tt>.</p>
     * @param {String} id
     * @returns {FormDSL}
     */
    form: function(id) {
        return getForm(id)._dsl || null;
    },
    
    /**
     * <p>Returns a DSL object for handling events related to the form with the
     * given <tt>id</tt>.</p>
     * @param {String} id
     * @returns {WhenDSL}
     */
    when: function(id) {
        return getForm(id)._when || null;
    },
    
    /**
     * <p>Returns a DSL object for applying pre-processing filters before events take place.</p>
     * @param {String} id
     * @returns {BeforeDSL}
     */
    before: function(id) {
        return getForm(id)._before || null;
    },
    
    /**
     * <p>Returns a helper function for use with <tt>when().isValidated()</tt>. The returned
     * function will display the forms elements as a bulleted list inside the element you
     * supply, in a <tt>div</tt> with the class name <tt>error-explanation</tt>.</p>
     * @param {String|HTMLElement|DomCollection} element
     * @returns {Function}
     */
    displayErrorsIn: function(element) {
        return function(errors) {
            element = element.setContent ? element : Ojay(element);
            var n = errors.length;
            if (n == 0) return element.setContent('');
            var were = (n == 1) ? 'was' : 'were', s = (n == 1) ? '' : 's';
            element.setContent(Ojay.HTML.div({className: 'error-explanation'}, function(HTML) {
                HTML.p('There ' + were + ' ' + n + ' error' + s + ' with the form:');
                HTML.ul(function(HTML) {
                    errors.map('message').forEach(HTML.method('li'));
                });
            }));
        };
    },
    
    /**
     * <p>Returns a helper function for use with <tt>when().responseArrives()</tt>. The returned
     * function will take the HTTP response body and display it in the specified element.</p>
     * @param {String|HTMLElement|DomCollection} element
     * @returns {Function}
     */
    displayResponseIn: function(element) {
        return function(response) {
            response.insertInto(element);
        };
    },
    
    EMAIL_FORMAT: Ojay.EMAIL_FORMAT
};

/**
 * <p>The <tt>FormDSL</tt> class creates DSL objects used to describe forms. Every
 * <tt>FormDescription</tt> instance has one of these objects that provides DSL-level
 * access to the description.</p>
 * @constructor
 * @class FormDSL
 * @private
 */
var FormDSL = new JS.Class(/** @scope FormDSL.prototype */{
    /**
     * @param {FormDescription} form
     */
    initialize: function(form) {
        this._form = form;
    },
    
    /**
     * <p>Returns a <tt>RequirementDSL</tt> object used to specify the requirement.</p>
     * @param {String} name
     * @param {String} displayed
     * @returns {RequirementDSL}
     */
    requires: function(name, displayed) {
        var requirement = this._form._getRequirement(name);
        if (displayed) this._form._displayNames[name] = displayed;
        return requirement._dsl;
    },
    
    /**
     * <p>Adds a validator function to the form that allows the user to inspect the data
     * and add new errors.</p>
     * @param {Function} block
     * @returns {FormDSL}
     */
    validates: function(block) {
        this._form._validators.push(block);
        return this;
    },
    
    /**
     * <p>Causes form submissions to be sent using Ajax rather than page-reloading requests.</p>
     * @param {Object} options
     * @returns {FormDSL}
     */
    submitsUsingAjax: function(options) {
        this._form._ajax = true;
        return this;
    },
    
    /**
     * <p>Causes the form to indicate which field in currently focused by applying a class
     * name to the focused input element.</p>
     * @returns {FormDSL}
     */
    highlightsActiveField: function() {
        this._form._highlightActiveField();
        return this;
    }
});

FormDSL.include({expects: FormDSL.prototype.requires});

var FormDSLMethods = ['requires', 'expects', 'validates', 'submitsUsingAjax', 'highlightsActiveField'];

/**
 * <p>The <tt>RequirementDSL</tt> class creates DSL objects used to describe form requirements.
 * All <tt>FormRequirement</tt> objects have one of these objects associated with them.</p>
 * @constructor
 * @class RequirementDSL
 * @private
 */
var RequirementDSL = new JS.Class(/** @scope RequirementDSL.prototype */{
    /**
     * @param {FormRequirement} requirement
     */
    initialize: function(requirement) {
        this._requirement = requirement;
    },
    
    /**
     * <p>Specifies that the given checkbox field must be checked.</p>
     * @param {String} message
     * @returns {RequirementDSL}
     */
    toBeChecked: function(message) {
        var requirement = this._requirement;
        this._requirement._add(function(value) {
            var element = requirement._elements.node;
            return (value == element.value && element.checked) || [message || 'must be checked'];
        });
        return this;
    },
    
    /**
     * <p>Specifies that the required field must be a number in order to be considered valid.</p>
     * @param {String} message
     * @returns {RequirementDSL}
     */
    toBeNumeric: function(message) {
        this._requirement._add(function(value) {
            return Ojay.isNumeric(value) || [message || 'must be a number'];
        });
        return this;
    },
    
    /**
     * <p>Specifies that the required field must have one of the values in the given list in
     * order to be considered valid.</p>
     * @param {Array} list
     * @param {String} message
     * @returns {RequirementDSL}
     */
    toBeOneOf: function(list, message) {
        this._requirement._add(function(value) {
            return list.indexOf(value) != -1 || [message || 'is not valid'];
        });
        return this;
    },
    
    /**
     * <p>Specifies that the required field must have none of the values in the given list in
     * order to be considered valid.</p>
     * @param {Array} list
     * @param {String} message
     * @returns {RequirementDSL}
     */
    toBeNoneOf: function(list, message) {
        this._requirement._add(function(value) {
            return list.indexOf(value) == -1 || [message || 'is not valid'];
        });
        return this;
    },
    
    /**
     * <p>Specifies that the required field must not be blank in order to be considered valid.
     * Calling this method is only necessary if you want a custom message for the rule, otherwise
     * a simple <tt>requires()</tt> will do.</p>
     * @param {String} message
     * @returns {RequirementDSL}
     */
    toBePresent: function(message) {
        this._requirement._add(function(value) {
            return !Ojay.isBlank(value) || [message || 'must not be blank'];
        });
        return this;
    },
    
    /**
     * <p>Specifies that the required field must confirm the value in another field.</p>
     * @param {String} field
     * @param {String} message
     * @returns {RequirementDSL}
     */
    toConfirm: function(field, message) {
        this._requirement._add(function(value, data) {
            return value == data.get(field) || [message || 'must be confirmed', field];
        });
        return this;
    },
    
    /**
     * <p>Specifies that the required field must have a certain length in order to be considered
     * valid. Valid inputs are a number (to specify an exact length), or an object with
     * <tt>minimum</tt> and <tt>maximum</tt> fields.</p>
     * @param {Number|Object} options
     * @param {String} message
     * @returns {RequirementDSL}
     */
    toHaveLength: function(options, message) {
        var min = options.minimum, max = options.maximum;
        this._requirement._add(function(value) {
            return  (typeof options == 'number' && value.length != options &&
                        [message || 'must contain exactly ' + options + ' characters']) ||
                    (min !== undefined && value.length < min &&
                        [message || 'must contain at least ' + min + ' characters']) ||
                    (max !== undefined && value.length > max &&
                        [message || 'must contain no more than ' + max + ' characters']) ||
                    true;
        });
        return this;
    },
    
    /**
     * <p>Specifies that the required field must have a certain value in order to be considered
     * valid. Input should be an object with <tt>minimum</tt> and <tt>maximum</tt> fields.</p>
     * @param {Object} options
     * @param {String} message
     * @returns {RequirementDSL}
     */
    toHaveValue: function(options, message) {
        var min = options.minimum, max = options.maximum;
        this._requirement._add(function(value) {
            if (!Ojay.isNumeric(value)) return [message || 'must be a number'];
            value = Number(value);
            return  (min !== undefined && value < min &&
                        [message || 'must be at least ' + min]) ||
                    (max !== undefined && value > max &&
                        [message || 'must not be greater than ' + max]) ||
                    true;
        });
        return this;
    },
    
    /**
     * <p>Specifies that the required field must match a given regex in order to be considered
     * valid.</p>
     * @param {Regexp} format
     * @param {String} message
     * @returns {RequirementDSL}
     */
    toMatch: function(format, message) {
        this._requirement._add(function(value) {
            return format.test(value) || [message || 'is not valid'];
        });
        return this;
    }
});

RequirementDSL.include(FormDSLMethods.reduce(function(memo, method) {
    memo[method] = function() {
        var base = this._requirement._form._dsl;
        return base[method].apply(base, arguments);
    };
    return memo;
}, {}));

/**
 * <p>The <tt>WhenDSL</tt> class creates DSL objects used to describe form requirements. All
 * <tt>FormDescription</tt> objects have one of these objects associated with them. The WhenDSL
 * is used specifically to describe events linked to forms.</p>
 * @constructor
 * @class WhenDSL
 * @private
 */
var WhenDSL = new JS.Class(/** @scope WhenDSL.prototype */{
    /**
     * @param {FormDescription} form
     */
    initialize: function(form) {
        this._form = form;
    },
    
    /**
     * <p>Allows a hook to be registered to say what should be done with the list of error
     * messages when a particular form is validated.</p>
     * @param {Function} block
     * @param {Object} context
     */
    isValidated: function(block, context) {
        this._form.subscribe(function(form) {
            block.call(context || null, form._errors._messages());
        });
    },
    
    /**
     * <p>Registers a function to handle the HTTP response when an Ajax form submission completes.</p>
     * @param {Function} block
     * @param {Object} context
     */
    responseArrives: function(block, context) {
        block = Function.from(block);
        if (context) block = block.bind(context);
        this._form._ajaxResponders.push(block);
    }
});

/**
 * <p>The <tt>BeforeDSL</tt> class creates DSL objects used to describe pre-processing actions. All
 * <tt>FormDescription</tt> objects have one of these objects associated with them.</p>
 * @constructor
 * @class BeforeDSL
 * @private
 */
var BeforeDSL = new JS.Class({
    /**
     * @param {FormDescription} form
     */
    initialize: function(form) {
        this._form = form;
    },
    
    /**
     * @param {Function} block
     */
    isValidated: function(block) {
        this._form._dataFilters.push(block);
    }
});

/**
 * <p>The <tt>Inputable</tt> module is mixed into <tt>Forms.Select</tt>, and indirectly into
 * <tt>Forms.Checkbox</tt> and <tt>Forms.RadioButtons.Item</tt> through <tt>Checkable</tt>.
 * It provides methods for setting class names on form elements to indicate the hovered, focused
 * and disabled states of form inputs.</p>
 * @module Inputable
 * @private
 */
var Inputable = new JS.Module(/** @scope Inputable */{
    include: Ojay.Observable,
    
    /**
     * <p>Called inside class constructors to set up the behaviour of the form input and
     * its associated label. Hides the input off the page, and sets up a set of events to
     * enable class names to be changed.</p>
     */
    _setupInput: function() {
        var wrapper = Ojay( Ojay.HTML.span() ).setStyle({position: 'relative'});
        this._input.insert(wrapper.node, 'before');
        wrapper.insert(this._input.node, 'bottom');
        this._input.setStyle({position: 'absolute', left: '-5000px', top: 0});
        
        this._input.on('focus')._(this).setFocused(true);
        this._input.on('blur')._(this).setFocused(false);
        
        this._label = Ojay.Forms.getLabel(this._input);
        if (this._label.node) this._label.addClass(this._inputType);
        
        this._interface = [this._input, this._label];
        if (this.getHTML) this._interface.push(this.getHTML());
        this._interface.forEach(it().on('mouseover')._(this).setHovered(true));
        this._interface.forEach(it().on('mouseout')._(this).setHovered(false));
        this._interface.forEach(it().addClass('js'));
        
        this.setDisabled();
    },
    
    /**
     * <p>Adds or removes the class name 'focused' from the input and its label depending on <tt>state</tt>.</p>
     * @param {Boolean} state
     * @returns {Inputable}
     */
    setFocused: function(state) {
        if (this._input.node.checked) this.setChecked();
        this._setClass(state, 'focused');
        return this;
    },
    
    /**
     * <p>Adds or removes the class name 'focused' from the input and its label depending on <tt>state</tt>.</p>
     * @param {Boolean} state
     * @returns {Inputable}
     */
    setHovered: function(state) {
        this._setClass(state, 'hovered');
        return this;
    },
    
    /**
     * <p>Adds or removes the class name 'disabled' from the input and its label depending on <tt>state</tt>.</p>
     * @param {Boolean} state
     * @returns {Inputable}
     */
    setDisabled: function(state) {
        this.disabled = (state === undefined) ? this._input.node.disabled : !!state;
        this._input.node.disabled = this.disabled;
        this._setClass(this.disabled, 'disabled');
        return this;
    },
    
    /**
     * <p>Adds or removes a class name from the input's elements according to its state.</p>
     * @param {Boolean} state
     * @param {String} name
     */
    _setClass: function(state, name) {
        this._stateClasses = this._stateClasses || [];
        if (state) {
            if (this._stateClasses.indexOf(name) == -1) this._stateClasses.push(name);
            this._stateClasses.sort();
        } else {
            this._stateClasses = this._stateClasses.filter(function(s) { return s != name });
        }
        
        this._interface.forEach(it()[state ? 'addClass' : 'removeClass'](name));
        var classes = this._interface[0].node.className.split(/\s+/);
        
        var type = this._inputType, pattern = new RegExp('^' + type + '-');
        
        var stateClass = classes.filter({match: pattern})[0];
        if (stateClass) this._interface.forEach({removeClass: stateClass});
        if (this._stateClasses.length) this._interface.forEach({addClass: type + '-' + this._stateClasses.join('-')});
    }
});

/**
 * <p>The <tt>Checkable</tt> module extends <tt>Inputable</tt> by providing methods to
 * handle checking and unchecking of form elements. It is used by the <tt>Forms.Checkbox</tt>
 * and <tt>Forms.RadioButtons.Item</tt> classes to add and remove class names from their
 * associated <tt>label</tt> tags.</p>
 * @private
 * @module Checkable
 */
var Checkable = new JS.Module(/** @scope Checkable */{
    include: Inputable,
    
    /**
     * <p>Called inside class constructors to set up the behaviour of a form input and its label.
     * Causes the input and its label to add/remove the 'checked' class name to indicate the state
     * of the input.</p>
     */
    _setupButton: function() {
        this._setupInput();
        this._input.on('click')._(this).setChecked()._(this._input.node).focus();
        this.setChecked();
    },
    
    /**
     * <p>Adds or removes the class name 'checked' from the input and its label depending on whether the
     * input is checked. If the input is part of a <tt>RadioButtons</tt> group, notifies the group in
     * order to change the state of the currently checked input.</p>
     * @param {Boolean} state
     * @param {Boolean} notify
     * @returns {Checkable}
     */
    setChecked: function(state, notify) {
        var oldChecked = !!this.checked;
        this.checked = (state === undefined) ? this._input.node.checked : !!state;
        if (this._group) {
            if (this.checked) {
                this._input.node.checked = true;
                this._group._check(this, notify);
            }
        } else {
            this._input.node.checked = this.checked;
            if (notify !== false && oldChecked != this.checked)
                this.notifyObservers('change');
        }
        this._setClass(this.checked, 'checked');
        return this;
    },
    
    /**
     * <p>Returns <tt>true</tt> iff the element is checked.</p>
     * @returns {Boolean}
     */
    isChecked: function() {
        return !!this.checked;
    }
});

JS.MethodChain.addMethod('focus');

/**
 * <p>The <tt>Forms.RadioButtons</tt> class can be used to 'hijack' sets of radio buttons to
 * make them easier to style using CSS. The radio inputs themselves become hidden (they are positioned
 * off-screen rather than hidden using <tt>display</tt> or <tt>visibility</tt>) and their labels
 * have their class names changed to mirror changes to the inputs as the user interacts with the form.</p>
 *
 * <p>This class is designed as a light-weight and unobtrusive replacement for <tt>YAHOO.widget.ButtonGroup</tt>
 * for the simple case where you want to style your form inputs and retain programmatic access to them.
 * It encourages accessible markup through use of <tt>label</tt> elements, and does not alter the HTML
 * structure of your form in any way.</p>
 *
 * @constructor
 * @class Forms.RadioButtons
 */
Ojay.Forms.RadioButtons = new JS.Class(/** @scope Forms.RadioButtons.prototype */{
    include: Ojay.Observable,
    
    /**
     * @param {String|HTMLElement|DomCollection} inputs
     */
    initialize: function(inputs) {
        this._items = Ojay(inputs).map(function(input) { return new this.klass.Item(this, input); }, this);
        if (this._items.map('_input.node.name').unique().length > 1)
            throw new Error('Attempt to create a RadioButtons object with radios of different names');
        this._checkedItem = this._items.filter('checked')[0] || null;
    },
    
    /**
     * <p>This method is used to make sure that only one input appears checked at any time. Items
     * must notify their group when they become checked so the group can uncheck the previously
     * checked item.</p>
     * @param {Forms.RadioButtons.Item} item
     * @param {Boolean} notify
     */
    _check: function(item, notify) {
        var current = this._checkedItem;
        if (current && current != item) current.setChecked(false);
        if (notify !== false && current != item) this.notifyObservers('change');
        this._checkedItem = item;
    },
    
    /**
     * <p>Returns the <tt>Item</tt> in the <tt>RadioButtons</tt> group with the given id or value.</p>
     * @param {String|Number} id
     * @returns {Forms.RadioButtons.Item}
     */
    getItem: function(id) {
        return this._items.filter(function(item) {
            return item._input.node.id == id || item._input.node.value == id;
        })[0];
    },
    
    /**
     * @returns {DomCollection}
     */
    getInput: function() {
        return Ojay(this._items.map('_input.node'));
    },
    
    /**
     * @returns {DomCollection}
     */
    getLabel: function() {
        return Ojay(this._items.map('_label.node'));
    },
    
    /**
     * <p>Returns the current value of the radio button group.</p>
     * @returns {String}
     */
    getValue: function() {
        var item = this._items.filter('_input.node.checked')[0];
        return item ? item._input.node.value : null;
    },
    
    /**
     * <p>Sets the value of the radio button group to the given <tt>value</tt>, if a button
     * with that value exists.</p>
     * @param {String} value
     * @param {Boolean} notify
     * @returns {Forms.RadioButtons}
     */
    setValue: function(value, notify) {
        var input = this.getItem(value);
        if (input) input.setChecked(true, notify);
        return this;
    },
    
    extend: /** @scope Forms.RadioButtons */{
        /**
         * @constructor
         * @class Forms.RadioButtons.Item
         */
        Item: new JS.Class(/** @scope Forms.RadioButtons.Item.prototype */{
            include: Checkable,
            _inputType: 'radio',
            
            /**
             * @param {Forms.RadioButtons} group
             * @param {DomCollection} input
             */
            initialize: function(group, input) {
                styledInputs.push(this);
                if (!input || !input.node || input.node.type != 'radio')
                    throw new TypeError('Attempt to create a RadioButtons object with non-radio element');
                this._group = group;
                this._input = input;
                this._setupButton();
            }
        })
    }
});

/**
 * <p>The <tt>Forms.Checkbox</tt> class can be used to 'hijack' checkbox inputs in HTML forms to
 * make them easier to style using CSS. The checkbox inputs themselves become hidden (they are positioned
 * off-screen rather than hidden using <tt>display</tt> or <tt>visibility</tt>) and their labels
 * have their class names changed to mirror changes to the inputs as the user interacts with the form.</p>
 *
 * <p>This class is designed as a light-weight and unobtrusive replacement for <tt>YAHOO.widget.Button</tt>
 * for the simple case where you want to style your form inputs and retain programmatic access to them.
 * It encourages accessible markup through use of <tt>label</tt> elements, and does not alter the HTML
 * structure of your form in any way.</p>
 *
 * @constructor
 * @class Forms.Checkbox
 */
Ojay.Forms.Checkbox = new JS.Class(/* @scope Forms.Checkbox.prototype */{
    include: Checkable,
    _inputType: 'checkbox',
    
    /**
     * @param {String|HTMLElement|DomCollection} input
     */
    initialize: function(input) {
        styledInputs.push(this);
        this._input = Ojay(input);
        if (!this._input || !this._input.node || this._input.node.type != 'checkbox')
            throw new TypeError('Attempt to create a Checkbox object with non-checkbox element');
        this._setupButton();
    },
    
    /**
     * @returns {DomCollection}
     */
    getInput: function() {
        return this._input;
    },
    
    /**
     * @returns {DomCollection}
     */
    getLabel: function() {
        return this._label;
    }
});

Ojay.Forms.Checkbox.include({
    getValue:   Ojay.Forms.Checkbox.prototype.isChecked,
    setValue:   Ojay.Forms.Checkbox.prototype.setChecked
});

/**
 * <p>The <tt>Forms.Select</tt> class can be used to 'hijack' drop-down menu inputs in HTML forms to
 * make them easier to style using CSS. The select inputs themselves become hidden (they are positioned
 * off-screen rather than hidden using <tt>display</tt> or <tt>visibility</tt>) and their labels
 * have their class names changed to mirror changes to the inputs as the user interacts with the form.</p>
 *
 * <p>This class is designed as a light-weight and unobtrusive replacement for <tt>YAHOO.widget.Button</tt>
 * for the simple case where you want to style your form inputs and retain programmatic access to them.
 * It encourages accessible markup through use of <tt>label</tt> elements, and does not alter the HTML
 * structure of your form in any way.</p>
 *
 * @constructor
 * @class Forms.Select
 */
Ojay.Forms.Select = new JS.Class(/** @scope Forms.Select.prototype */{
    include: [JS.State, Inputable],
    _inputType: 'select',
    
    extend: /** @scope Forms.Select */{
        CONTAINER_CLASS:    'select-container',
        DISPLAY_CLASS:      'select-display',
        BUTTON_CLASS:       'select-button',
        LIST_CLASS:         'select-list',
        
        /**
         * @constructor
         * @class Forms.Select.Option
         */
        Option: new JS.Class(/** @scope Forms.Select.Option.prototype */{
            /**
             * @param {Forms.Select} select
             * @param {HTMLElement} option
             */
            initialize: function(select, option) {
                this._select = select;
                this._option = Ojay(option);
                this.value = option.value || '';
                this._label = option.text.stripTags();
                this.hovered = false;
                
                var element = this.getHTML();
                [element.on('mouseover'), element.on('mousemove')]
                        .forEach(it()._(this).setHovered(true));
            },
            
            /**
             * <p>Returns an Ojay collection wrapping the list item used to display the option.</p>
             * @returns {DomCollection}
             */
            getHTML: function() {
                if (this._html) return this._html;
                return this._html = Ojay( Ojay.HTML.li(this._label) );
            },
            
            /**
             * <p>Sets the option to be hovered, and notified its parent <tt>Select</tt> instance
             * so it can un-hover the currently hovered option.</p>
             * @param {Boolean} state
             * @returns {Forms.Select.Option}
             */
            setHovered: function(state) {
                this.hovered = (state !== false);
                if (this.hovered) {
                    this._select._setHoveredOption(this);
                    this._nudgeIntoView();
                }
                this.getHTML()[state === false ? 'removeClass' : 'addClass']('hovered');
                return this;
            },
            
            /**
             * <p>Makes sure the option is in view if the list container has a fixed height
             * and is using <tt>overflow: scroll</tt>.</p>
             */
            _nudgeIntoView: function() {
                var list = this._select._elements._listContainer;
                var listRegion = list.getRegion(), myRegion = this.getHTML().getRegion();
                if (listRegion.contains(myRegion)) return;
                var scroll = list.node.scrollTop || 0, edge = (myRegion.top > listRegion.top) ? 'bottom' : 'top';
                list.node.scrollTop = scroll + myRegion[edge] - listRegion[edge];
            }
        })
    },
    
    /**
     * @param {String|HTMLElement|DomCollection} select
     */
    initialize: function(select) {
        styledInputs.push(this);
        this._input = Ojay(select);
        if (!this._input || this._input.node.tagName.toLowerCase() != 'select')
            throw new TypeError('Attempt to create a Select object with non-select element');
        var elements = this._elements = {};
        this._input.insert(this.getHTML().node, 'after');
        this._setupInput();
        this.updateOptions();
        
        this.setState('LIST_OPEN');
        this.hideList(false);
        
        this._input.on('blur')._(this).hideList(true);
        
        // Wait a little bit because 'keydown' fires before the value changes
        [this._input.on('keydown'), this._input.on('change')]
                .forEach(it().wait(0.001)._(this)._updateDisplayFromSelect(false));
        
        this._input.on('keydown', function(element, evnt) {
            var code = evnt.keyCode || 0;
            if (code.between(48,57) || code.between(65,90) || code.between(37,40))
                this.wait(0.001).showList();
        }, this);
        
        elements._container.setStyle({position: 'relative', cursor: 'default'});
        [elements._display, elements._button].forEach(it().on('click')._(this).toggleList());
        
        var KeyListener = YAHOO.util.KeyListener;
        new KeyListener(this._input.node, {keys: KeyListener.KEY.ESCAPE}, {
            fn: this.method('hideList').partial(false)
        }).enable();
        new KeyListener(this._input.node, {keys: KeyListener.KEY.ENTER}, {
            fn: this.method('hideList').partial(true)
        }).enable();
        
        elements._listContainer.setStyle({position: 'absolute'});
    },
    
    /**
     * <p>Returns an Ojay collection wrapping the HTML used as a stand-in for the
     * <tt>select</tt> input.</p>
     * @returns {DomCollection}
     */
    getHTML: function() {
        var elements = this._elements, klass = this.klass;
        if (elements._container) return elements._container;
        return elements._container = Ojay( Ojay.HTML.div({className: this.klass.CONTAINER_CLASS}, function(HTML) {
            elements._display = Ojay( HTML.div({className: klass.DISPLAY_CLASS}) );
            elements._button = Ojay( HTML.div({className: klass.BUTTON_CLASS}) );
            elements._listContainer = Ojay( HTML.div({className: klass.LIST_CLASS}, function(HTML) {
                elements._list = Ojay( HTML.ul() );
            }) );
        }) );
    },
    
    /**
     * @returns {DomCollection}
     */
    getInput: function() {
        return this._input;
    },
    
    /**
     * @returns {DomCollection}
     */
    getLabel: function() {
        return this._label;
    },
    
    /**
     * <p>Focuses the <tt>select</tt> element.</p>
     * @returns {Forms.Select}
     */
    _focusInput: function() {
        this._input.node.focus();
    },
    
    /**
     * <p>Refreshes the list of displayed options. Use this method if you change the
     * contents of the <tt>select</tt> element.</p>
     * @returns {Forms.Select}
     */
    updateOptions: function() {
        this._elements._list.setContent('');
        this._options = Array.from(this._input.node.options).map(function(option) {
            option = new this.klass.Option(this, option);
            this._elements._list.insert(option.getHTML().node);
            return option;
        }, this);
        this._updateDisplayFromSelect();
        return this;
    },
    
    /**
     * <p>Updates the UI of the instance in response to the current state of the
     * underlying <tt>select</tt> input.</p>
     * @param {Boolean} notify
     */
    _updateDisplayFromSelect: function(notify) {
        var oldValue = this._currentValue;
        var selected = this.getSelectedOption();
        if (!selected) return;
        this._elements._display.setContent(selected.text.stripTags());
        this._getOption(selected.value).setHovered(true);
        if (this.inState('LIST_OPEN') || notify === false) return;
        this._currentValue = selected.value;
        if (oldValue !== undefined && oldValue != this._currentValue)
            this.notifyObservers('change');
    },
    
    /**
     * <p>Returns the <tt>Select.Option</tt> instance with the given value.</p>
     * @param {String} value
     * @returns {Forms.Select.Option}
     */
    _getOption: function(value) {
        return this._options.filter({value: value})[0] || null;
    },
    
    /**
     * <p>Sets the given <tt>Select.Option</tt> to be hovered, and removes hover state from
     * all other options.</p>
     * @param {Forms.Select.Option}
     */
    _setHoveredOption: function(option) {
        if (this._currentOption) this._currentOption.setHovered(false);
        this._currentOption = option;
    },
    
    /**
     * <p>Returns an array of references to <tt>option</tt> elements.</p>
     * @returns {Array}
     */
    _getOptions: function() {
        return Array.from(this._input.node.options);
    },
    
    /**
     * <p>Returns a reference to the currently selected <tt>option</tt> element, or a
     * reference to the first element if none is selected.</p>
     * @returns {HTMLElement}
     */
    getSelectedOption: function() {
        return this._getOptions().filter('selected')[0] || this._input.node.options[0] || null;
    },
    
    /**
     * <p>Returns all the <tt>option</tt> elements in the <tt>select</tt> whose value equals
     * the supplied <tt>value</tt>.</p>
     * @param {String|Number} value
     * @returns {Array}
     */
    getOptionsByValue: function(value) {
        return this._getOptions().filter({value: value});
    },
    
    /**
     * <p>Returns the current value of the <tt>select</tt> element.</p>
     * @returns {String}
     */
    getValue: function() {
        return this.getSelectedOption().value;
    },
    
    /**
     * <p>Sets the value of the <tt>select</tt> element to the given <tt>value</tt>, triggering
     * a <tt>change</tt> event unless you pass <tt>false</tt> as the second parameter.</p>
     * @param {String|Number} value
     * @param {Boolean} notify
     * @returns {Forms.Select}
     */
    setValue: function(value, notify) {
        Ojay.Forms.setValue(this._input, value);
        this._updateDisplayFromSelect(notify);
        return this;
    },
    
    /**
     * <p>Sets the position of the list relative to the container so the two are properly aligned.</p>
     * @returns {Forms.Select}
     */
    updateListPosition: function() {
        var region = this._elements._container.getRegion();
        if (!region) return this;
        var list = this._elements._listContainer;
        list.setStyle({width: region.getWidth() + 'px', left: 0, top: region.getHeight() + 'px'});
        return this;
    },
    
    states: {
        LIST_CLOSED: /** @scope Forms.Select.prototype */{
            /**
             * <p>Displays the drop-down list.</p>
             * @returns {Forms.Select}
             */
            showList: function() {
                if (this.disabled) return this;
                this.updateListPosition();
                this._elements._listContainer.show();
                this.setState('LIST_OPEN');
                this._focusInput();
                var selected = this.getSelectedOption();
                if (selected) this._getOption(selected.value).setHovered(true);
                return this;
            },
            
            /**
             * <p>Displays the drop-down list.</p>
             * @returns {Forms.Select}
             */
            toggleList: function() {
                return this.showList();
            }
        },
        
        LIST_OPEN: /** @scope Forms.Select.prototype */{
            /**
             * <p>Hides the drop-down list.</p>
             * @param {Boolean} update
             * @returns {Forms.Select}
             */
            hideList: function(update) {
                this._elements._listContainer.hide();
                this.setState('LIST_CLOSED');
                if (update !== false) {
                    this.setValue(this._currentOption.value);
                    this._focusInput();
                }
                return this;
            },
            
            /**
             * <p>Hides the drop-down list.</p>
             * @param {Boolean} update
             * @returns {Forms.Select}
             */
            toggleList: function(update) {
                return this.hideList(update);
            }
        }
    }
});

})();
