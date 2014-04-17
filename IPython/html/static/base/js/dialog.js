//----------------------------------------------------------------------------
//  Copyright (C) 2013  The IPython Development Team
//
//  Distributed under the terms of the BSD License.  The full license is in
//  the file COPYING, distributed as part of this software.
//----------------------------------------------------------------------------

//============================================================================
// Utility for modal dialogs with bootstrap
//============================================================================

IPython.namespace('IPython.dialog');

IPython.dialog = (function (IPython) {
    "use strict";
    
    var modal = function (options) {
        // <div class="modal fade" id="myModal" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
        //   <div class="modal-dialog">
        //     <div class="modal-content">
        //       <div class="modal-header">
        //         <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
        //         <h4 class="modal-title" id="myModalLabel">Modal title</h4>
        //       </div>
        //       <div class="modal-body">
        //         ...
        //       </div>
        //       <div class="modal-footer">
        //         <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>
        //         <button type="button" class="btn btn-primary">Save changes</button>
        //       </div>
        //     </div>
        //   </div>
        // </div>

        var modal = $("<div/>")
            .addClass("modal")
            .addClass("fade")
            .attr("role", "dialog");
        var dialog = $("<div/>")
            .addClass("modal-dialog")
            .appendTo(modal);
        var dialog_content = $("<div/>")
            .addClass("modal-content")
            .appendTo(dialog);
        dialog_content.append(
            $("<div/>")
                .addClass("modal-header")
                .append($("<button>")
                    .attr("type", "button")
                    .addClass("close")
                    .attr("data-dismiss", "modal")
                    .attr("aria-hidden", "true")
                    .html("&times;")
                ).append(
                    $("<h4/>")
                        .addClass('modal-title')
                        .text(options.title || "")
                )
        ).append(
            $("<div/>").addClass("modal-body").append(
                options.body || $("<p/>")
            )
        );
        
        var footer = $("<div/>").addClass("modal-footer");
        
        for (var label in options.buttons) {
            var btn_opts = options.buttons[label];
            var button = $("<button/>")
                .addClass("btn btn-default")
                .attr("data-dismiss", "modal")
                .text(label);
            if (btn_opts.click) {
                button.click($.proxy(btn_opts.click, dialog_content));
            }
            if (btn_opts.class) {
                button.addClass(btn_opts.class);
            }
            footer.append(button);
        }
        dialog_content.append(footer);
        // hook up on-open event
        modal.on("shown", function() {
            setTimeout(function() {
                footer.find("button").last().focus();
                if (options.open) {
                    $.proxy(options.open, modal)();
                }
            }, 0);
        });
        
        // destroy modal on hide, unless explicitly asked not to
        if (options.destroy === undefined || options.destroy) {
            modal.on("hidden", function () {
                modal.remove();
            });
        }
        modal.on("hidden", function () {
            if (IPython.notebook) {
                var cell = IPython.notebook.get_selected_cell();
                if (cell) cell.select();
                IPython.keyboard_manager.enable();
                IPython.keyboard_manager.command_mode();
            }
        });
        
        if (IPython.keyboard_manager) {
            IPython.keyboard_manager.disable();
        }
        
        return modal.modal(options);
    };

    var edit_metadata = function (md, callback, name) {
        name = name || "Cell";
        var error_div = $('<div/>').css('color', 'red');
        var message = 
            "Manually edit the JSON below to manipulate the metadata for this " + name + "." +
            " We recommend putting custom metadata attributes in an appropriately named sub-structure," +
            " so they don't conflict with those of others.";

        var textarea = $('<textarea/>')
            .attr('rows', '13')
            .attr('cols', '80')
            .attr('name', 'metadata')
            .text(JSON.stringify(md || {}, null, 2));
        
        var dialogform = $('<div/>').attr('title', 'Edit the metadata')
            .append(
                $('<form/>').append(
                    $('<fieldset/>').append(
                        $('<label/>')
                        .attr('for','metadata')
                        .text(message)
                        )
                        .append(error_div)
                        .append($('<br/>'))
                        .append(textarea)
                    )
            );
        var editor = CodeMirror.fromTextArea(textarea[0], {
            lineNumbers: true,
            matchBrackets: true,
            indentUnit: 2,
            autoIndent: true,
            mode: 'application/json',
        });
        IPython.dialog.modal({
            title: "Edit " + name + " Metadata",
            body: dialogform,
            buttons: {
                OK: { class : "btn-primary",
                    click: function() {
                        // validate json and set it
                        var new_md;
                        try {
                            new_md = JSON.parse(editor.getValue());
                        } catch(e) {
                            console.log(e);
                            error_div.text('WARNING: Could not save invalid JSON.');
                            return false;
                        }
                        callback(new_md);
                    }
                },
                Cancel: {}
            }
        });
        editor.refresh();
    };
    
    return {
        modal : modal,
        edit_metadata : edit_metadata,
    };

}(IPython));
