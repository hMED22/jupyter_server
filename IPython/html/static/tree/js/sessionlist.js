// Copyright (c) IPython Development Team.
// Distributed under the terms of the Modified BSD License.

define([
    'base/js/namespace',
    'components/jquery/jquery.min',
    'base/js/utils',
    'base/js/events',
], function(IPython, $, Utils, Events) {
    "use strict";

    var SesssionList = function (options) {
        this.sessions = {};
        this.base_url = options.base_url || Utils.get_body_data("baseUrl");
    };
    
    SesssionList.prototype.load_sessions = function(){
        var that = this;
        var settings = {
            processData : false,
            cache : false,
            type : "GET",
            dataType : "json",
            success : $.proxy(that.sessions_loaded, this),
            error : Utils.log_ajax_error,
        };
        var url = Utils.url_join_encode(this.base_url, 'api/sessions');
        $.ajax(url, settings);
    };

    SesssionList.prototype.sessions_loaded = function(data){
        this.sessions = {};
        var len = data.length;
        var nb_path;
        for (var i=0; i<len; i++) {
            nb_path = Utils.url_path_join(
                data[i].notebook.path,
                data[i].notebook.name
            );
            this.sessions[nb_path] = data[i].id;
        }
        Events.trigger('sessions_loaded.Dashboard', this.sessions);
    };

    // Backwards compatability.
    IPython.SesssionList = SesssionList;

    return SesssionList;
});
