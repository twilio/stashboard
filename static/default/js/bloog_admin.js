/**
 The MIT License
 
 Copyright (c) 2008 William T. Katz
 
 Permission is hereby granted, free of charge, to any person obtaining a copy
 of this software and associated documentation files (the "Software"), to 
 deal in the Software without restriction, including without limitation 
 the rights to use, copy, modify, merge, publish, distribute, sublicense, 
 and/or sell copies of the Software, and to permit persons to whom the 
 Software is furnished to do so, subject to the following conditions:
 
 The above copyright notice and this permission notice shall be included in
 all copies or substantial portions of the Software.
 
 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
 DEALINGS IN THE SOFTWARE.
**/

YAHOO.bloog.initAdmin = function() {

    var showRTE = function(e) {
        var hdr = $('div#postDialog div.hd');
        YAHOO.bloog.http = {};
        switch (this.id) {
            case 'updatestatus':
                hdr.setContent('Update Status');
                YAHOO.bloog.http.action = '/status';
                YAHOO.bloog.http.verb = 'POST';
                YAHOO.bloog.postUpdateStatus.render();
                YAHOO.bloog.postUpdateStatus.show();
                break;
            case 'newblog':
                hdr.setContent('Submit Blog Entry');
                var today = new Date();
                var month = today.getMonth() + 1;
                var year = today.getFullYear();
                YAHOO.bloog.http.action = "/" + year + "/" + month;
                YAHOO.bloog.http.verb = 'POST';
                YAHOO.bloog.editor.setEditorHTML('<p>Blog entry goes here</p>');
                YAHOO.bloog.postDialog.render();
                YAHOO.bloog.postDialog.show();
                break;
            case 'editbtn':
                hdr.setContent('Submit Edit');
                YAHOO.bloog.http.action = '?_method=PUT';
                YAHOO.bloog.http.verb = 'POST';
                // Get the current article content and populate the dialog
                YAHOO.util.Connect.initHeader('Accept', 'application/json');
                YAHOO.util.Connect.asyncRequest('GET', '#', {
                    success: YAHOO.bloog.populateDialog,
                    failure: YAHOO.bloog.handleFailure
                }, null);
                break;
        }
    }

    YAHOO.bloog.populateDialog = function(o) {
        var article = eval('(' + o.responseText + ')')
        document.getElementById("postTitle").value = article.title;
        if (article.tags) {
            document.getElementById("postTags").value = article.tags.join(', ');
        }
        YAHOO.bloog.editor.setEditorHTML(article.body);
        YAHOO.bloog.postDialog.render();
        YAHOO.bloog.postDialog.show();
    }
    
    var submitRequest = function(postData){
        var cObj = YAHOO.util.Connect.asyncRequest(
            YAHOO.bloog.http.verb, 
            YAHOO.bloog.http.action, 
            { success: YAHOO.bloog.handleSuccess, 
              failure: YAHOO.bloog.handleFailure },
            postData);
    }
    
    var handleUpdateStatus = function() {
        var options = YAHOO.util.Dom.get('statusMenu');
        var status = "";
        for (var i=0; i < options.length; i++) {
            if(options[i].selected){
                status = options[i].value;
            }
        };
        var postData = 'status=' + encodeURIComponent(status);
        submitRequest(postData);
    }

    var handleSubmit = function() {
        YAHOO.bloog.editor.saveHTML();
        var html = YAHOO.bloog.editor.get('element').value;
        var title = YAHOO.util.Dom.get('postTitle').value;
        var tags = YAHOO.util.Dom.get('postTags').value;
        var postData = 'title=' + encodeURIComponent(title) + '&' +
                       'tags=' + encodeURIComponent(tags) + '&' +
                       'body=' + encodeURIComponent(html);
        submitRequest(postData);
    }
    


    YAHOO.bloog.postDialog = new YAHOO.widget.Dialog(
        "postDialog", {
            width: "520px",
            fixedcenter: true,
            visible: false,
            modal: true,
            constraintoviewpoint: true,
            buttons: [ { text: "Submit", handler: handleSubmit, 
                         isDefault:true },
                       { text: "Cancel", handler: YAHOO.bloog.handleCancel } ]
        });
        
    YAHOO.bloog.postUpdateStatus = new YAHOO.widget.Dialog(
        "postUpdateStatus", {
            width: "520px",
            fixedcenter: true,
            visible: false,
            modal: true,
            constraintoviewpoint: true,
            buttons: [ { text: "Submit", handler: handleUpdateStatus, 
                         isDefault:true },
                       { text: "Cancel", handler: YAHOO.bloog.handleCancel } ]
        });

    YAHOO.bloog.postDialog.validate = function() {
        var data = this.getData();
        if (data.postTitle == "") {
            alert("Please enter a title for this post.");
            return false;
        }
        return true;
    }
    YAHOO.bloog.postDialog.callback = { success: YAHOO.bloog.handleSuccess, 
                                        failure: YAHOO.bloog.handleFailure };

    YAHOO.bloog.editor = new YAHOO.widget.Editor('postBody', {
        height: '250px',
        width: '500px',
        dompath: true,
        animate: true,
        toolbar: {
            titlebar: '',
            draggable: true,
            buttonType: 'advanced',
            buttons: [
                /*** Prefer to have blog articles of one font and use consistent sizing
                { group: 'fontstyle', label: 'Font Name and Size',
                    buttons: [
                        { type: 'select', label: 'Arial', value: 'fontname', disabled: true,
                            menu: [
                                { text: 'Arial', checked: true },
                                { text: 'Arial Black' },
                                { text: 'Comic Sans MS' },
                                { text: 'Courier New' },
                                { text: 'Lucida Console' },
                                { text: 'Tahoma' },
                                { text: 'Times New Roman' },
                                { text: 'Trebuchet MS' },
                                { text: 'Verdana' }
                            ]
                        },
                        { type: 'spin', label: '13', value: 'fontsize', range: [ 9, 75 ], disabled: true }
                    ]
                },
                { type: 'separator' },
                ***/
                { group: 'textstyle', label: 'Font Style',
                    buttons: [
                        { type: 'push', label: 'Bold CTRL + SHIFT + B', value: 'bold' },
                        { type: 'push', label: 'Italic CTRL + SHIFT + I', value: 'italic' },
                        { type: 'push', label: 'Underline CTRL + SHIFT + U', value: 'underline' },
                        { type: 'separator' },
                        { type: 'push', label: 'Subscript', value: 'subscript', disabled: true },
                        { type: 'push', label: 'Superscript', value: 'superscript', disabled: true },
                        { type: 'separator' },
                        { type: 'color', label: 'Font Color', value: 'forecolor', disabled: true },
                        { type: 'color', label: 'Background Color', value: 'backcolor', disabled: true },
                        { type: 'separator' },
                        { type: 'push', label: 'Remove Formatting', value: 'removeformat', disabled: true },
                        { type: 'push', label: 'Show/Hide Hidden Elements', value: 'hiddenelements' }
                    ]
                },
                { type: 'separator' },
                { group: 'alignment', label: 'Alignment',
                    buttons: [
                        { type: 'push', label: 'Align Left CTRL + SHIFT + [', value: 'justifyleft' },
                        { type: 'push', label: 'Align Center CTRL + SHIFT + |', value: 'justifycenter' },
                        { type: 'push', label: 'Align Right CTRL + SHIFT + ]', value: 'justifyright' },
                        { type: 'push', label: 'Justify', value: 'justifyfull' }
                    ]
                },
                { type: 'separator' },
                { group: 'parastyle', label: 'Paragraph Style',
                    buttons: [
                    { type: 'select', label: 'Normal', value: 'heading', disabled: true,
                        menu: [
                            { text: 'Normal', value: 'none', checked: true },
                            { text: 'Header 1', value: 'h1' },
                            { text: 'Header 2', value: 'h2' },
                            { text: 'Header 3', value: 'h3' },
                            { text: 'Header 4', value: 'h4' }
                        ]
                    }
                    ]
                },
                { type: 'separator' },
                { group: 'indentlist', label: 'Indenting and Lists',
                    buttons: [
                        { type: 'push', label: 'Indent', value: 'indent', disabled: true },
                        { type: 'push', label: 'Outdent', value: 'outdent', disabled: true },
                        { type: 'push', label: 'Create an Unordered List', value: 'insertunorderedlist' },
                        { type: 'push', label: 'Create an Ordered List', value: 'insertorderedlist' }
                    ]
                },
                { type: 'separator' },
                { group: 'insertcode', label: 'Insert Code',
                    buttons: [
                    { type: 'push', label: 'Python', value: 'pythonbtn', disabled: false },
                    { type: 'push', label: 'Javascript', value: 'jsbtn', disabled: false },
                    { type: 'push', label: 'Ruby', value: 'rubybtn', disabled: false },
                    { type: 'push', label: 'PHP', value: 'phpbtn', disabled: false },
                    { type: 'push', label: 'XML/HTML', value: 'htmlbtn', disabled: false },
                    { type: 'push', label: 'CSS', value: 'cssbtn', disabled: false },
                    ]
                },
                { type: 'separator' },
                { group: 'insertitem', label: 'Insert Item',
                    buttons: [
                        { type: 'push', label: 'HTML Link CTRL + SHIFT + L', value: 'createlink', disabled: true },
                        { type: 'push', label: 'Insert Image', value: 'insertimage' }
                    ]
                }
            ]
        }
    });

    //Use the toolbarLoaded Custom Event; when that event fires,
    //we will execute a function that adds the code buttons:
    YAHOO.bloog.editor.on('toolbarLoaded', function() {

        // Now listen for the new buttons click and do something with it.
        // Note that the clicks are events synthesized for us automatically
        // because those are the values we gave our buttons above:
        this.toolbar.on('pythonbtnClick', function(o) {
            this.execCommand('inserthtml', '<p></p><pre name="code" class="python"># Python code here</pre><p></p>');
        }, YAHOO.bloog.editor, true);
        this.toolbar.on('jsbtnClick', function(o) {
            this.execCommand('inserthtml', '<p></p><pre name="code" class="js">// Javascript code here</pre><p></p>');
        }, YAHOO.bloog.editor, true);
        this.toolbar.on('rubybtnClick', function(o) {
            this.execCommand('inserthtml', '<p></p><pre name="code" class="ruby"># Ruby code here</pre><p></p>');
        }, YAHOO.bloog.editor, true);
        this.toolbar.on('phpbtnClick', function(o) {
            this.execCommand('inserthtml', '<p></p><pre name="code" class="php">// PHP code here</pre><p></p>');
        }, YAHOO.bloog.editor, true);
        this.toolbar.on('cssbtnClick', function(o) {
            this.execCommand('inserthtml', '<p></p><pre name="code" class="css">/* CSS code here */</pre><p></p>');
        }, YAHOO.bloog.editor, true);
        this.toolbar.on('htmlbtnClick', function(o) {
            this.execCommand('inserthtml', '<p></p><pre name="code" class="html">&lt;!-- XML/HTML code here --></pre><p></p>');
        }, YAHOO.bloog.editor, true);
        /**
        //Setup the button to be enabled, disabled or selected
        this.on('afterNodeChange', function(o) {
            //Get the selected element
            var el = this._getSelectedElement();

            //Get the button we want to manipulate
            var button = this.toolbar.getButtonByValue('pythonbtn');

            if (el && el.tagName == 'div') {
                this.toolbar.enableButton(button);
            }
        }, this, true);
        **/
    }, YAHOO.bloog.editor, true);

    YAHOO.bloog.editor.render();
    YAHOO.bloog.postDialog.showEvent.subscribe(YAHOO.bloog.editor.show,
                                               YAHOO.bloog.editor, true);
    YAHOO.bloog.postDialog.hideEvent.subscribe(YAHOO.bloog.editor.hide,
                                               YAHOO.bloog.editor, true);

    var handleDelete = function() {
        var cObj = YAHOO.util.Connect.asyncRequest(
            'DELETE',
            '#', 
            { success: YAHOO.bloog.handleSuccess, 
              failure: YAHOO.bloog.handleFailure }
        );
    }
    YAHOO.bloog.deleteDialog = new YAHOO.widget.SimpleDialog(
        "confirmDlg", {
            width: "20em",
            effect: { effect:YAHOO.widget.ContainerEffect.FADE, duration:0.25 },
            fixedcenter: true,
            modal: true,
            visible: false,
            draggable: false,
            buttons: [ { text: "Delete!", handler: handleDelete },
                       { text: "Cancel", 
                         handler: function () { this.hide(); },
                         isDefault: true } ]
        })
    YAHOO.bloog.deleteDialog.setHeader("Warning");
    YAHOO.bloog.deleteDialog.setBody("Are you sure you want to delete this post?");
    YAHOO.bloog.deleteDialog.render(document.body);
    
    YAHOO.util.Event.on("updatestatus", "click", showRTE);
    YAHOO.util.Event.on("newblog", "click", showRTE);
    YAHOO.util.Event.on("editbtn", "click", showRTE);
    YAHOO.util.Event.on("deletebtn", "click", function (e) { YAHOO.bloog.deleteDialog.show(); });
}

YAHOO.util.Event.onDOMReady(YAHOO.bloog.initAdmin);
