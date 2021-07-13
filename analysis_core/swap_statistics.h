#ifndef SWAP_STATISTICS2_H
#define SWAP_STATISTICS2_H

#include <vector>
#include <tuple>
#include <map> 
#include <iostream>
#include <future>

#include "frequency_counter.h"


template<typename T, size_t... Is>
void add_rhs_to_lhs(T& t1, const T& t2, std::integer_sequence<size_t, Is...>)
{
    auto l = { (std::get<Is>(t1) += std::get<Is>(t2), 0)... };
    (void)l; 
}

template <typename...T>
std::tuple<T...>& operator += (std::tuple<T...>& lhs, const std::tuple<T...>& rhs)
{
    add_rhs_to_lhs(lhs, rhs, std::index_sequence_for<T...>{});
    return lhs;
}

template <typename...T>
std::tuple<T...> operator + (std::tuple<T...> lhs, const std::tuple<T...>& rhs)
{
   return lhs += rhs;
}


template<class S, auto (S::* ... Args)()>
class swap_statistics {
    public:
    const unsigned n_reference_sets;
    std::tuple<         decltype((std::declval<S>().*Args)())           ...> original_value;
    std::tuple<frequency_counter<decltype((std::declval<S>().*Args)())>...> freqs;

    template<typename X>
    using Double = double;

    static constexpr int freq_member = 0;
    static constexpr int original_value_member = 1;
    static constexpr int p_member = 2;

    std::tuple<Double<decltype((std::declval<S>().*Args)())> ...> p;

    swap_statistics(const S &s, unsigned n_reference_sets): 
        n_reference_sets{n_reference_sets}
    {
        S s_copy(s);
        eval<0, original_value_member, Args ...>(s_copy);
        for(unsigned i = 0; i < n_reference_sets; i++) {
            s_copy.swap_in_place();
            eval<0, freq_member, Args ...>(s_copy);
        }
        eval<0, p_member, Args ...>(s_copy);
    }

    swap_statistics(const S &s, unsigned n_reference_sets, unsigned n_threads):
        n_reference_sets{n_reference_sets}
    {
        S s_copy(s);
        eval<0, original_value_member, Args ...>(s_copy);        
        unsigned n_per_thread = n_reference_sets / n_threads;
        unsigned n_residual   = n_reference_sets - (n_per_thread * n_threads);
        std::vector<std::future<swap_statistics<S, Args ...>>> threads;
        for(unsigned i = 0; i < n_threads - 1; i++) {
            auto run = [s, n_per_thread](){return swap_statistics<S, Args...>(s, n_per_thread);};
            threads.push_back(std::async(std::launch::async, run));
        }
        auto stat = swap_statistics<S, Args...>(s, n_residual + n_per_thread);
        freqs = freqs + stat.freqs;
        for(auto &t : threads) {
            freqs = freqs + t.get().freqs;
        }
        eval<0, p_member, Args ...>(s_copy);        
    }

    template<int i, typename Val_Type, int member, auto (S::*func)()>
    void operate(S &s)
    {
        if constexpr(member == freq_member) {
            auto val = (s.*func)();
            std::get<i>(freqs)[val]++;
        } 
        if constexpr(member == original_value_member) {
            auto val = (s.*func)();
            std::get<i>(original_value) = val;
        }
        if constexpr(member == p_member) {
            compute_p<i>();
        }
    }

    template<int i, int member,
             auto (S::*func)()>
    void eval(S &s) {
        operate<i, decltype((std::declval<S>().*func)()), member, func>(s);
    }

    template<int i, int member, 
             auto (S::*func1)(), auto (S::*func2)(), auto (S::* ... Args1)()>
    void eval(S &s) {
        operate<i, decltype((std::declval<S>().*func1)()), member, func1>(s);
        eval<i + 1, member, func2, Args1 ...>(s);
    }

    template<int i>
    void compute_p()
    {
        std::get<i>(p) = std::get<i>(freqs).get_p(std::get<i>(original_value));
    }

    template<int i>
    std::string tidy_table() const
    {
        std::string name = "p = " + std::to_string(std::get<i>(p));
        return std::get<i>(freqs).tidy_table(name, std::get<i>(original_value));
    }
};


template<class S, typename Arg_t, typename Ret_t, std::vector<Ret_t> (S::*fun)(const std::vector<Arg_t>&) const>
class swap_statistics_dynamic {
    public:
    const unsigned n_reference_sets;
    std::vector<Ret_t> original_value;
    std::vector<frequency_counter<Ret_t>> freqs;
    std::vector<double> p;

    swap_statistics_dynamic(const S &s, unsigned n_reference_sets, const std::vector<Arg_t> &args): 
        n_reference_sets{n_reference_sets}
    {
        S s_copy(s);
        original_value = (s_copy.*fun)(args);
        freqs.reserve(args.size());
        for(auto a: args) {
            freqs.push_back(frequency_counter<Ret_t>());
        }
        for(unsigned i = 0; i < n_reference_sets; i++) {
            s_copy.swap_in_place();

            std::vector<Ret_t> vals = (s_copy.*fun)(args);
            for(unsigned j = 0; j < args.size(); j++) {
                freqs[j][vals[j]]++;
            }
        }

        compute_p();
    }

    swap_statistics_dynamic(const S &s, unsigned n_reference_sets, const std::vector<Arg_t> &args,
                            unsigned n_threads): 
        n_reference_sets{n_reference_sets}
    {
        S s_copy(s);
        original_value = (s_copy.*fun)(args);
        for(auto a: args) {
            freqs.push_back(frequency_counter<Ret_t>());
        }
        unsigned n_per_thread = n_reference_sets / n_threads;
        unsigned n_residual   = n_reference_sets - (n_per_thread * n_threads);

        std::vector<std::future<swap_statistics_dynamic<S, Arg_t, Ret_t, fun>>> threads;
        for(unsigned i = 0; i < n_threads - 1; i++) {
            auto run = [s_copy, n_per_thread, args](){
                return swap_statistics_dynamic<S, Arg_t, Ret_t, fun>(s_copy, n_per_thread, args);
            };

            threads.push_back(std::async(std::launch::async, run));

        }
        auto stat = swap_statistics_dynamic<S, Arg_t, Ret_t, fun>(s_copy, n_residual + n_per_thread, args);

        for(unsigned i = 0; i < original_value.size(); i++) {
            freqs[i] += stat.freqs[i];
        }
        for(auto &t : threads) {
            auto t_freqs = t.get().freqs;
            for(unsigned i = 0; i < original_value.size(); i++) {
                freqs[i] += t_freqs[i];
            }
        }
        compute_p();
    }

    void compute_p()
    {
        for(unsigned i = 0; i < original_value.size(); i++)
            p.push_back(compute_p(i));
    }

    double compute_p(int i)
    {
        return freqs[i].get_p(original_value[i]);
    }

    std::string tidy_table(int i, Arg_t arg) const
    {
        std::string name = arg.to_string() + " p = " + std::to_string(p[i]);
        return freqs[i].tidy_table(name, original_value[i]);
    }

    std::string tidy_table(std::vector<Arg_t> args) const
    {
        std::string ret;
        for(unsigned i = 0; i < args.size(); i++)
            ret += tidy_table(i, args[i]);
        return ret;
    }
};

#endif
