import activationfn as acfn

data=[-3, -1, 0, 2, 5]

acfn.benchmarks(data,"math")
acfn.benchmarks(data,"posit8")
acfn.benchmarks(data,"float8")
acfn.benchmarks(data,"posit16")
acfn.benchmarks(data,"float16")
acfn.benchmarks(data,"posit32")
acfn.benchmarks(data,"float32")
acfn.benchmarks(data,"posit64")
acfn.benchmarks(data,"float64")