// Test widget bool class
casper.notebook_test(function () {
    index = this.append_cell(
        'from IPython.html import widgets\n' + 
        'from IPython.display import display, clear_output\n' +
        'print("Success")');
    this.execute_cell_then(index);

    var bool_index = this.append_cell(
        'bool_widget = widgets.BoolWidget(description="Title", value=True)\n' +
        'display(bool_widget)\n'+
        'display(bool_widget, view_name="ToggleButtonView")\n' +
        'print("Success")');
    this.execute_cell_then(bool_index, function(index){

        this.test.assert(this.get_output_cell(index).text == 'Success\n', 
            'Create bool widget cell executed with correct output.');

        this.test.assert(this.cell_element_exists(index, 
            '.widget-area .widget-subarea'),
            'Widget subarea exists.');

        this.test.assert(this.cell_element_exists(index, 
            '.widget-area .widget-subarea .widget-hbox-single input'),
            'Checkbox exists.');

        this.test.assert(this.cell_element_function(index, 
            '.widget-area .widget-subarea .widget-hbox-single input', 'prop', ['checked']),
            'Checkbox is checked.');

        this.test.assert(this.cell_element_exists(index, 
            '.widget-area .widget-subarea .widget-hbox-single .widget-hlabel'),
            'Checkbox label exists.');

        this.test.assert(this.cell_element_function(index, 
            '.widget-area .widget-subarea .widget-hbox-single .widget-hlabel', 'html')=="Title",
            'Checkbox labeled correctly.');

        this.test.assert(this.cell_element_exists(index, 
            '.widget-area .widget-subarea div button'),
            'Toggle button exists.');

        this.test.assert(this.cell_element_function(index, 
            '.widget-area .widget-subarea div button', 'html')=="Title",
            'Toggle button labeled correctly.');

        this.test.assert(this.cell_element_function(index, 
            '.widget-area .widget-subarea div button', 'hasClass', ['active']),
            'Toggle button is toggled.');

    });

    index = this.append_cell(
        'bool_widget.value = False\n' +
        'print("Success")');
    this.execute_cell_then(index, function(index){

        this.test.assert(this.get_output_cell(index).text == 'Success\n', 
            'Change bool widget value cell executed with correct output.');

        this.test.assert(! this.cell_element_function(bool_index, 
            '.widget-area .widget-subarea .widget-hbox-single input', 'prop', ['checked']),
            'Checkbox is not checked. (1)');

        this.test.assert(! this.cell_element_function(bool_index, 
            '.widget-area .widget-subarea div button', 'hasClass', ['active']),
            'Toggle button is not toggled. (1)');

        // Try toggling the bool by clicking on the toggle button.
        this.cell_element_function(bool_index, '.widget-area .widget-subarea div button', 'click');

        this.test.assert(this.cell_element_function(bool_index, 
            '.widget-area .widget-subarea .widget-hbox-single input', 'prop', ['checked']),
            'Checkbox is checked. (2)');

        this.test.assert(this.cell_element_function(bool_index, 
            '.widget-area .widget-subarea div button', 'hasClass', ['active']),
            'Toggle button is toggled. (2)');
 
        // Try toggling the bool by clicking on the checkbox.
        this.cell_element_function(bool_index, '.widget-area .widget-subarea .widget-hbox-single input', 'click');

        this.test.assert(! this.cell_element_function(bool_index, 
            '.widget-area .widget-subarea .widget-hbox-single input', 'prop', ['checked']),
            'Checkbox is not checked. (3)');

        this.test.assert(! this.cell_element_function(bool_index, 
            '.widget-area .widget-subarea div button', 'hasClass', ['active']),
            'Toggle button is not toggled. (3)');

    });
});