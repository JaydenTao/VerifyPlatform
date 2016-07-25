/*global openerp, _, $ */

openerp.web_searchview_custom = function (instance) {

    instance.web.ViewManager.include({

        setup_search_view: function(view_id, search_defaults) {
        var self = this;
        if (this.searchview) {
            this.searchview.destroy();
        }

        var options = {
            hidden: this.flags.search_view === false,
            disable_custom_filters: this.flags.search_disable_custom_filters,
        };
        this.searchview = new instance.web.SearchView(this, this.dataset, view_id, search_defaults, options);

        this.searchview.on('search_data', self, this.do_searchview_search);
        return this.searchview.appendTo(this.$(".oe_view_manager_view_search"),
                                      this.$(".oe_searchview_drawer_container"));
    },


    });

}
