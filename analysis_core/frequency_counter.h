#ifndef FREQUENCY_COUNTER_H
#define FREQUENCY_COUNTER_H

#include <map>
#include <string>
#include <iostream>

template<typename T>
class frequency_counter{
    public:

    std::map<T, unsigned> freqs;


    unsigned& operator[](T key)
    {
        return freqs[key];
    }

    frequency_counter& operator+=(const frequency_counter<T> &a)
    {
        for(auto [val, freq]: a.freqs)
            freqs[val] += freq;
        return *this;
    }

    double get_p(T sample) const
    {
        unsigned freq_larger  = 0;
        unsigned freq_smaller = 0;
        unsigned freq_total   = 0;
        for(auto const& [val, freq]: freqs) {
            if(val < sample)
                freq_smaller += freq;
            else if(val > sample)
                freq_larger  += freq;
            else
                freq_total   += freq;

        }
        freq_total += freq_smaller + freq_larger;
        return (1.0 / double(freq_total + 1)) * 
               double(std::min(freq_smaller, freq_larger + 1));
    }

    std::string tidy_table(std::string name, T sample) const
    {
        std::string ret = "Name,Value,freq,original\n";
        for(auto const& [val, freq]: freqs) {
            ret += name                        + ',' + 
                   std::to_string(val)         + ',' + 
                   std::to_string(freq)        + ',' + 
                   (val == sample ? 'T' : 'F') + '\n';
        }
        return ret;
    }
};

template<typename T>
frequency_counter<T> operator+(frequency_counter<T> &a, frequency_counter<T> &b)
{
    frequency_counter<T> ret;
    ret += a;
    ret += b;
    return ret;
}

#endif
