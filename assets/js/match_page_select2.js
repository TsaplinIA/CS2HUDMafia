$("select.team-selector", document).each(function () {
    let el = $(this);
    el.select2({
        allowClear: true,
        ajax: {
            url: el.data("url"),
            dataType: "json",
            width: '100%',
            data: function (params) {
                return {
                    skip: ((params.page || 1) - 1) * 20,
                    limit: 20,
                    select2: true,
                    where: params.term,
                    order_by: el.data("pk") + " asc",
                };
            },
            processResults: function (data, params) {
                return {
                    results: $.map(data.items, function (obj) {
                        obj.id = obj[el.data("pk")];
                        return obj;
                    }),
                    pagination: {
                        more: (params.page || 1) * 20 < data.total,
                    },
                };
            },
            cache: true,
        },
        minimumInputLength: 0,
        templateResult: function (item) {
            if (!item.id) return "Search...";
            return $(item._meta.select2.result);
        },
        templateSelection: function (item) {
            if (!item.id) return "Search...";
            if (item._meta) return $(item._meta.select2.selection);
            return $(item.text);
        },
    });
    data = el.data("initial");
    if (data)
        $.ajax({
        url: el.data("url"),
            data: {
                select2: true,
                pks: data,
            },
            traditional: true,
            dataType: "json",
        }).then(function (data) {
            for (obj of data.items) {
                obj.id = obj[el.data("pk")];
                var option = new Option(
                    obj._meta.select2.selection,
                    obj.id,
                    true,
                    true
                );
                el.append(option).trigger("change");
                el.trigger({
                    type: "select2:select",
                    params: {
                        data: obj,
                    },
                });
            }
      });
});