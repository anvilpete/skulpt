var $builtinmodule = function (name) {
    var mod = {};

    mod.get_filename = new Sk.builtin.func(function (tb) {
        return new Sk.builtin.str(tb.$getFilename());
    });

    mod.get_name = new Sk.builtin.func(function (tb) {
        return new Sk.builtin.str(tb.$getFuncname());
    });

    mod.get_line = new Sk.builtin.func(function (tb) {
        var line = tb.$getLine();
        return line !== null ? new Sk.builtin.str(line) : Sk.builtin.none.none$;
    });

    return mod;
};
