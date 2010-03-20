/*
Copyright (c) 2007-2008 the OTHER media Limited
Licensed under the BSD license, http://ojay.othermedia.org/license.html
*/
// @require ojay/core-min
/**
 * @overview
 * <p>The <tt>Mouse</tt> module, when included in a web page, automatically keeps track
 * of the current mouse position by listening to the document's <tt>mousemove</tt> event. You
 * can grab the current mouse position from anywhere in your code by checking the <tt>left</tt> and
 * <tt>top</tt> properties of <tt>Ojay.Mouse.position</tt>.</p>
 *
 * <p>You can also use <tt>Mouse</tt> to listen for <tt>mouseenter</tt> and <tt>mouseleave</tt>
 * events, which are like <tt>mouseover</tt> and <tt>mouseout</tt> except without the problems
 * caused by missed events and nested elements. When <tt>Mouse</tt> is present on a page,
 * you can register event listeners as follows:</p>
 *
 * <pre><code>    Ojay('p').on('mouseenter', function(element, position) {
 *         // respond to event
 *     }, scope);</code></pre>
 *
 * <p>Within your callback function, <tt>element</tt> refers to the element the mouse entered,
 * and <tt>position</tt> is an object whose <tt>left</tt> and <tt>top</tt> properties represent
 * the position of the mouse at the time of the event. The optional <tt>scope</tt> argument sets
 * the meaning of <tt>this</tt> inside your callback.</p>
 *
 * <p>More generally, you can subscribe to all mouse movement as follows:</p>
 *
 * <pre><code>    Ojay.Mouse.subscribe(function(position) {
 *         // respond to mouse movement with
 *         // position.left and position.top
 *     }, scope);</code></pre>
 *
 * <p>Your callback is fired every time the mouse moves, and it is given the mouse position in
 * the <tt>position</tt> argument. Again, use <tt>scope</tt> to set the meaning of <tt>this</tt>
 * inside the callback.</p>
 */
Ojay.Mouse = new JS.Singleton(/** @scope Ojay.Mouse */{
    include: JS.Observable,
    
    initialize: function() {
        this.position = {left: null, top: null};
    },
    
    /**
     * <p>Callback used to respond to mousemove events. Calls <tt>notifyObservers</tt> with
     * the current mouse position.</p>
     * @param {Event} e
     */
    updatePosition: function(doc, e) {
        var xy = YAHOO.util.Event.getXY(e);
        this.position = {left: xy[0], top: xy[1]};
        this.notifyObservers(this.position);
    },
    
    /**
     * <p>Provides support for detecting events when the mouse pointer enters or leaves an
     * element, in a way that doesn't cause the problems of mouseover/mouseout. Firstly, the
     * mouse pointer is monitored across the whole document, so you've less chance of missing
     * a mouseout event due to fast movement. Second, this function will not fire a mouse-out
     * event if you mouse over an element nested inside the element you're listening to.</p>
     *
     * @param {String} movement Either 'entering' or 'leaving'
     * @param {Region|HTMLElement|String} element The element to watch for mouse events
     * @param {Function} callback A function to fire
     * @param {Object} scope The scope in which to fire the callback (optional)
     */
    on: function(movement, element, callback, scope) {
        if (!/^(?:entering|leaving)$/.test(movement))
            throw new TypeError('Movement is not recognised');
        
        var isRegion    = (element instanceof Ojay.Region);
        var region      = isRegion ? element : null;
        var element     = isRegion ? null: Ojay(element);
        var wasInside   = false;
        this.addObserver(function(position) {
            var currentRegion = region || element.getRegion();
            var isInside = this.isInside(currentRegion);
            if (movement == 'entering' && !wasInside && isInside)
                callback.call(scope || null, this.position);
            if (movement == 'leaving' && wasInside && !isInside)
                callback.call(scope || null, this.position);
            wasInside = isInside;
        }, this);
    },
    
    /**
     * <p>Returns <tt>true</tt> iff the mouse pointer is currently inside the given region or
     * element. <tt>region</tt> can be an HTML element reference or a CSS selector, in which
     * case the test region will be the area of the first element that matches the selector.
     * Returns <tt>undefined</tt> if no region can be found.</p>
     * @param {Region|HTMLElement|String} region
     * @returns {Boolean}
     */
    isInside: function(region) {
        region = Ojay.Region.convert(region);
        if (!region) return undefined;
        var pos = this.position;
        return pos.left >= region.left && pos.left <= region.right &&
                pos.top >= region.top && pos.top <= region.bottom;
    }
});

Ojay(document).on('mousemove', Ojay.Mouse.method('updatePosition'));

/**
 * <p><tt>DomCollection#on</tt> is wrapped to provide <tt>mouseenter</tt> and <tt>mouseleave</tt>
 * event detection support.</p>
 */
Ojay.DomCollection.include({on: Ojay.DomCollection.prototype.on.wrap(function() {
    var args = Array.from(arguments), original = args.shift();
    var eventName = args[0], callback = args[1], scope = args[2];
    
    if (!/^mouse(enter|leave)$/.test(eventName))
        return original(eventName, callback, scope);
        
    var type = eventName.match(/^mouse(enter|leave)$/)[1].replace(/e?$/, 'ing');
    var collector = new JS.MethodChain();
    if (callback && typeof callback != 'function') scope = callback;
    
    this.forEach(function(element) {
        Ojay.Mouse.on(type, element, function(position) {
            if (typeof callback == 'function') callback.call(scope || null, element, position);
            collector.fire(scope || element);
        });
    });
    
    return collector;
})});
