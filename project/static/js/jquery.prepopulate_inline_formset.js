;(function($) {
    $.fn.prefill = function(queryset)
    {
        function selectOption(element, value) {
            element.each(function( index ) {
                $( this ).removeAttr("selected");

                if ($( this ).val() == value) {
                  $( this ).attr("selected", '')
                };
            });
        }

        for (const [index, element] of queryset.slice(1).entries()) {
            $('.add-row')[0].click();
        }

        $('tbody tr').each(function( index ) {
            selectOption($( this, 'td:first div div select option' ).find('td:first div div select option'), queryset[index]);
        });
    };
})(jQuery);
