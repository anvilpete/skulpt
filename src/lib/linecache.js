var $builtinmodule = function (name) {
    var mod = {};

    mod.getline = new Sk.builtin.func(function (filename, lineno, module_globals) {
        var fn = Sk.ffi.remapToJs(filename);
        var ln = Sk.ffi.remapToJs(lineno);
        var src = Sk.__sourceCache && Sk.__sourceCache[fn];
        if (src && ln > 0 && ln <= src.length) {
            return new Sk.builtin.str(src[ln - 1] + "\n");
        }
        return new Sk.builtin.str("");
    });

    mod.clearcache = new Sk.builtin.func(function () {
        // We don't have a cache, so do nothing
    });

    mod.checkcache = new Sk.builtin.func(function (filename) {
        // We don't have a cache, so do nothing
    });

    mod.lazycache = new Sk.builtin.func(function (filename, module_globals) {
        // We don't have a cache, so do nothing
    });

    return mod;
};
