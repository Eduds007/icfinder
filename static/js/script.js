$(document).ready(function() {
    $('.balloon').on('click', function(e) {
      const checkbox = $(this).find('.hidden-checkbox');
      checkbox.prop('checked', !checkbox.prop('checked'));
      $(this).toggleClass('selected', checkbox.prop('checked'));
    });
  
    $('.balloon label').on('click', function(e) {
      e.stopPropagation();
      const balloon = $(this).closest('.balloon');
      const checkbox = balloon.find('.hidden-checkbox');
      checkbox.prop('checked', !checkbox.prop('checked'));
      balloon.toggleClass('selected', checkbox.prop('checked'));
    });
  });