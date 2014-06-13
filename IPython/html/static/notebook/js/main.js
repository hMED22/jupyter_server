// Copyright (c) IPython Development Team.
// Distributed under the terms of the Modified BSD License.

var ipython = ipython || {};
require([
    'base/js/namespace',
    'components/jquery/jquery.min',
    'notebook/js/notebook',
    'base/js/utils',
    'base/js/page',
    'notebook/js/layoutmanager',
    'base/js/events',
    'auth/js/loginwidget',
    'notebook/js/maintoolbar',
    'notebook/js/pager',
    'notebook/js/quickhelp',
    'notebook/js/menubar',
    'notebook/js/notificationarea',
    'notebook/js/keyboardmanager',
], function(
    IPython, 
    $,
    Notebook, 
    Utils, 
    Page, 
    LayoutManager, 
    Events,
    LoginWidget, 
    MainToolBar, 
    Pager, 
    QuickHelp, 
    MenuBar, 
    NotificationArea, 
    KeyboardManager
    ) {
    "use strict";

    $('#ipython-main-app').addClass('border-box-sizing');
    $('div#notebook_panel').addClass('border-box-sizing');

    var opts = {
        base_url : Utils.get_body_data("baseUrl"),
        notebook_path : Utils.get_body_data("notebookPath"),
        notebook_name : Utils.get_body_data('notebookName')
    };

    page = new Page();
    layout_manager = new LayoutManager();
    keyboard_manager = new KeyboardManager();
    events = $([new Events()]);
    pager = new Pager('div#pager', 'div#pager_splitter', layout_manager, events);
    layout_manager.pager = pager;
    notebook = new Notebook('div#notebook', opts, events, keyboard_manager);
    login_widget = new LoginWidget('span#login_widget', opts);
    toolbar = new MainToolBar('#maintoolbar-container', notebook, events);
    quick_help = new QuickHelp(undefined, keyboard_manager, events);
    menubar = new MenuBar('#menubar', opts);

    notification_area = new NotificationArea('#notification_area');
    notification_area.init_notification_widgets();

    layout_manager.do_resize();

    $('body').append('<div id="fonttest"><pre><span id="test1">x</span>'+
                     '<span id="test2" style="font-weight: bold;">x</span>'+
                     '<span id="test3" style="font-style: italic;">x</span></pre></div>');
    var nh = $('#test1').innerHeight();
    var bh = $('#test2').innerHeight();
    var ih = $('#test3').innerHeight();
    if(nh != bh || nh != ih) {
        $('head').append('<style>.CodeMirror span { vertical-align: bottom; }</style>');
    }
    $('#fonttest').remove();

    page.show();

    layout_manager.do_resize();
    var first_load = function () {
        layout_manager.do_resize();
        var hash = document.location.hash;
        if (hash) {
            document.location.hash = '';
            document.location.hash = hash;
        }
        notebook.set_autosave_interval(notebook.minimum_autosave_interval);
        // only do this once
        events.off('notebook_loaded.Notebook', first_load);
    };
    
    events.on('notebook_loaded.Notebook', first_load);
    events.trigger('app_initialized.NotebookApp');
    notebook.load_notebook(opts.notebook_name, opts.notebook_path);

    ipython.page = page;
    ipython.layout_manager = layout_manager;
    ipython.notebook = notebook;
    ipython.pager = pager;
    ipython.quick_help = quick_help;
    ipython.login_widget = login_widget;
    ipython.menubar = menubar;
    ipython.toolbar = toolbar;
    ipython.notification_area = notification_area;
    ipython.events = events;
    ipython.keyboard_manager = keyboard_manager;
});
