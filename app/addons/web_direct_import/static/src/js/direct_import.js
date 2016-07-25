openerp.web_direct_import = function(instance){
    var QWeb = instance.web.qweb;



    instance.web.DirectImport = instance.web.form.FormWidget.extend(instance.web.form.ReinitializeWidgetMixin, {
        template: 'DirectImport',
        events:{
            'change .oe_form_binary_file':'loaded_file'
        },
        init:function(field_manager, node){
            //node.attrs.type = node.attrs['data-button-type'];
            this.is_stat_button = /\boe_stat_button\b/.test(node.attrs['class']);
            this.icon_class = node.attrs.icon && "stat_button_icon fa " + node.attrs.icon + " fa-fw";
            this._super(field_manager, node);
            this.force_disabled = false;
            this.string = (this.node.attrs.string || '').replace(/_/g, '');
            if (JSON.parse(this.node.attrs.default_focus || "0")) {
                // TODO fme: provide enter key binding to widgets
                this.view.default_focus_button = this;
            }
            if (this.node.attrs.icon && (! /\//.test(this.node.attrs.icon))) {
                this.node.attrs.icon = '/web/static/src/img/icons/' + this.node.attrs.icon + '.png';
            }

            // import object id
            this.id = null;
            this.res_model = node.attrs.model || field_manager.model;
            this.save_type = node.attrs.save_type || 'json';
            this.Import = new instance.web.Model('direct.import');
        },
        start:function(){
            //this._super.apply(this, arguments);
            //
            //if (this.node.attrs.help || instance.session.debug) {
            //   this.do_attach_tooltip();
            //}
            var self = this;
            return $.when(
                this._super(),
                this.Import.call('create', [{
                    'res_model': this.res_model,
                    'save_type': this.save_type
                }]).done(function (id) {
                    self.id = id;
                    self.$('input[name=parent_id]').val(self.view.datarecord.id)
                    self.$('input[name=import_id]').val(id);
                    self.$('input[name=save_type]').val(self.save_type);
                    self.$('input[name=model]').val(self.res_model);

                })
            )
        },
        //- File & settings change section
        loaded_file: function () {
            this.$('.oe_import_button')
                    .prop('disabled', true);
            if (!this.$('input.oe_form_binary_file').val()) { return; }

            //this.$el.removeClass('oe_import_preview oe_import_error');
            jsonp(this.$el.find('form:first'), {
                url: '/direct_import/upload'
            }, this.proxy('uploaded_file'));
        },

        uploaded_file:function(){
            this.$('.oe_import_button')
                    .prop('disabled', false);
            $(window).trigger('direct_imported',arguments)
        }
    });

    //instance.web.form.widgets.add('direct_import','instance.web.DirectImport');
    instance.web.form.custom_widgets.add('direct_import', 'instance.web.DirectImport');

    /**
     * Safari does not deal well at all with raw JSON data being
     * returned. As a result, we're going to cheat by using a
     * pseudo-jsonp: instead of getting JSON data in the iframe, we're
     * getting a ``script`` tag which consists of a function call and
     * the returned data (the json dump).
     *
     * The function is an auto-generated name bound to ``window``,
     * which calls back into the callback provided here.
     *
     * @param {Object} form the form element (DOM or jQuery) to use in the call
     * @param {Object} attributes jquery.form attributes object
     * @param {Function} callback function to call with the returned data
     */
    function jsonp(form, attributes, callback) {
        attributes = attributes || {};
        var options = {jsonp: _.uniqueId('import_callback_')};
        window[options.jsonp] = function () {
            delete window[options.jsonp];
            callback.apply(null, arguments);
        };
        if ('data' in attributes) {
            _.extend(attributes.data, options);
        } else {
            _.extend(attributes, {data: options});
        }
        _.extend(attributes, {
            dataType: 'script',
        });
        $(form).ajaxSubmit(attributes);
    }

}

