#include <iostream>
#include <algorithm>
#include <string>
#include <functional>
#include <optional>
#include <set>
#include <map>
#include <unordered_set>
#include <regex>
#include <random>
#include <utility>
#include <experimental/filesystem>

#include <boost/math/special_functions/sign.hpp>
#include <boost/math/distributions/binomial.hpp>
#include <boost/program_options.hpp>

#include "rapidcsv.h"
#include "swap_statistics.h"

std::set<std::string>   reliableModalities = {"Skin", "Ia", "Ib"};
std::set<std::string> unreliableModalities = {"II", "Pyr"};
std::set<std::string> antidromicModalities = {"aMN", "LRN"};

std::random_device rd;

int n_threads = 12;

namespace fs = std::experimental::filesystem;
namespace po = boost::program_options;

class Activation{
    public:

    std::string modality;    
    int length;

    Activation(std::string modality, int length):
        modality(modality), length(length) {}
    
    Activation(std::string s)
    {
        std::replace(s.begin(), s.end(), '.', '-');
        std::regex r("([a-zA-Z]+)(-?[0-9])");
        std::smatch match;
        std::regex_search(s, match, r);
        if(match.size() != 3) {
            std::cout << "Matching failure \"" << s << '\"' << std::endl;
            assert(false);
        }
        modality = match.str(1);
        length =  std::stoi(match.str(2));
    }

    Activation(const Activation &a)
    {
        modality = a.modality;
        length = a.length;
    }

    std::optional<Activation> plusOne() const
    {
        if(length < 0)
            return std::nullopt;
        else
            return std::optional<Activation>
                        (Activation(modality, length + 1));
    }

    std::optional<Activation> minusOne() const
    {
        if(length < 0)
            return std::nullopt;
        else
            return std::optional<Activation>
                        (Activation(modality, -(std::abs(length) + 1)));
    }

    std::optional<Activation> plus(unsigned x, int sign) const
    {
        assert(sign == 1 || sign == -1);
        if(length < 0)
            return std::nullopt;
        if(x > 1 && sign == -1)
            return std::nullopt;
        else
            return std::optional<Activation>
                        (Activation(modality, sign * (length + x)));
    }

    friend bool operator== (const Activation &a1, const Activation &a2)
    {
        return a1.length == a2.length && a1.modality == a2.modality;
    }

    friend bool operator< (const Activation &a1, const Activation &a2)
    {
        if(a1.modality != a2.modality)
            return a1.modality < a2.modality;
        else
            return a1.length < a2.length;
    }

    std::string to_string() const
    {
        return modality + std::to_string(length);
    }
};

template<typename lhs_t, typename rhs_t = lhs_t>
struct rule{
    lhs_t lhs;
    rhs_t rhs;

    rule(lhs_t lhs, rhs_t rhs) : lhs(lhs), rhs(rhs) {}
    friend bool operator< (const rule<lhs_t, rhs_t> &r1, const rule<lhs_t, rhs_t> &r2)
    {
        if(r1.lhs == r2.lhs)
            return r1.rhs < r2.rhs;
        else
            return r1.lhs < r2.lhs;
    }

    friend bool operator== (const rule &a, const rule &b)
    {
        return a.lhs == b.lhs && a.rhs == b.rhs;
    }

    std::string to_string()
    {
        return lhs.to_string() + " => " + rhs.to_string();
    }
};


class Neuron{
    public:

    std::vector<Activation> Activations;
    std::string ID;

    Neuron(std::string ID,
           std::vector<Activation> &Activations):
    ID(ID)
    {
        this->Activations = std::vector<Activation>(Activations);
        std::sort(this->Activations.begin(), this->Activations.end());
    }

    Neuron(std::vector<std::string> &RawDataLine, 
           std::vector<std::string> &header)
    {
        for(unsigned i = 0; i < header.size(); i++) {
            if(header[i] == "ID") {
                ID = RawDataLine[i];
            } else if(RawDataLine[i] == "1" && header[i] != "depth" && header[i] != "") {
                Activation a = Activation(header[i]);
                if(reliableModalities.count(a.modality) > 0)
                    Activations.push_back(a);
            }

        }
        std::sort(Activations.begin(), Activations.end());
    }

    Neuron(const Neuron &n)
    {
        Activations = std::vector<Activation>(n.Activations);
        ID = std::string(n.ID);
    }

    std::string to_string() const
    {
        std::string res = ID;
        for(auto n: Activations) {res += " " + n.to_string();}
        return res;
    }

    friend bool operator== (const Neuron &n1, const Neuron &n2)
    {
        return n1.Activations == n2.Activations;
    }

    Neuron DownstreamFromExt() const
    {
        std::vector<Activation> newActivations;
        for(Activation a : Activations) {
            auto a_plusOne = a.plusOne();
            if(a_plusOne.has_value() && std::abs(a_plusOne.value().length) <= 4)
                newActivations.push_back(a_plusOne.value());
        }
        return Neuron(ID + "Ext+1", newActivations);
    }

    Neuron DownstreamFromInh() const
    {
        std::vector<Activation> newActivations;
        for(Activation a : Activations) {
            auto a_minusOne = a.minusOne();
            if(a_minusOne.has_value() && std::abs(a_minusOne.value().length) <= 4)
                newActivations.push_back(a_minusOne.value());
        }
        return Neuron(ID + "Inh+1", newActivations);

    }

    Neuron Downstream(unsigned x, int sign) const
    {
        std::vector<Activation> newActivations;        
        assert(sign == 1 || sign == -1);
        for(Activation a : Activations) {
            auto new_a = a.plus(x, sign);
            if(new_a.has_value() && std::abs(new_a.value().length) <= 4)
                newActivations.push_back(new_a.value());
        }
        return Neuron(ID + std::to_string(sign) +  "+" + std::to_string(x), newActivations); 
    }
    
    bool subset(const Neuron &a) const
    {
        return std::includes(a.Activations.begin(), a.Activations.end(),
                               Activations.begin(),   Activations.end());
    }

    bool hasActivation(const Activation &a) const
    {
        return std::find(Activations.begin(), Activations.end(), a) !=
               Activations.end();
    }

    void swap_Activation(Activation &a1, Neuron&n, Activation &a2)
    {
        std::swap(a1, a2);
        std::sort(this->Activations.begin(), this->Activations.end());
        std::sort(n.Activations.begin(), n.Activations.end());
    }

    std::vector<std::pair<Activation, Activation>> feed_forward_pred_activations() const
    {
        std::vector<std::pair<Activation, Activation>> ret;
        for(auto a: Activations) {
            unsigned max_length = std::abs(a.length);
            for(unsigned i = 1; i < max_length; i++) {
                 ret.push_back(std::make_pair(Activation(a.modality, i), a));
            }
        }
        return ret;
    }
};

class NeuronSet {
    std::vector<Neuron> neurons;

    public:

    NeuronSet(std::string path)
    {
        rapidcsv::LabelParams params(0, -1);
        rapidcsv::Document data(path, params);
        std::vector<std::string> header = data.GetColumnNames();
        for(unsigned i = 0; i < data.GetRowCount(); i++) {
            auto row = data.GetRow<std::string>(i);
            neurons.push_back(Neuron(row, header));
        }
    }

    template <auto fun1, auto fun2>
    unsigned countLoops()
    {
        unsigned count = 0;
        for(auto n1: neurons) {
            Neuron Inhibitor = (n1.*fun1)();
            for(auto n2: neurons) {
                Neuron Excitator = (n2.*fun2)();
                if(Inhibitor.subset(n2) && Excitator.subset(n1)) {
                    count++;
                    break;
                }
            }
        }
        return count;
    }

    unsigned count_unrecorded_feed_forward()
    {
        unsigned unrecorded = 0;
        for(const Neuron& n: neurons) {
            auto pred_activations = n.feed_forward_pred_activations();
            for(auto [a, a_original]: pred_activations) {
                bool matched = false;
                for(const Neuron& match_a: neurons) {
                    if(!match_a.hasActivation(a))
                        continue;

                    int sign = boost::math::sign(a_original.length);
                    int synapses_to_n = std::abs(a_original.length) - std::abs(a.length);
                    Neuron match_a_down = match_a.Downstream(synapses_to_n, sign);
                    if(!match_a_down.subset(n)) {
                        continue;
                    } else {
                        matched = true;
                        break;
                    }
                }
                if(!matched) {
                    unrecorded++;
                    std::cout << n.ID << a.modality << a.length << '\n'; // << a << a_original;
                    break;
                }
            }
        }
        return unrecorded;
    }

    std::string to_string()
    {
        std::string ret;
        for(auto neuron : neurons) { ret+=neuron.to_string() + "\n";}
        return ret;
    }

    std::string to_csv()
    {
        std::string ret;
        auto activations = all_Activations();
        ret += "ID";
        for(auto a : activations)
            ret += ',' + a.to_string();
        ret += '\n';
        for(auto neuron : neurons) {
            ret += neuron.ID;
            for(auto a : activations) {
                if(neuron.hasActivation(a))
                    ret += ",1";
                else
                    ret += ",0";
            }
            ret += '\n';
        }
        return ret;
    }

    std::map<Activation, unsigned> countModalitiyFrequencies()
    {
        std::map<Activation, unsigned> frequencies;
        for(auto n: neurons){
            for(auto a: n.Activations)
                frequencies[a]++;
        }
        return frequencies;
    }

    std::map<unsigned, unsigned> countActivationFrequencies()
    {
        std::map<unsigned, unsigned> frequencies;
        for(auto n: neurons){
            unsigned s = n.Activations.size();
            frequencies[s]++;
        }
        return frequencies;
    }

    std::string frequencies_to_string()
    {
        std::string ret;
        auto ModalitiyFrequencies  = countModalitiyFrequencies();
        auto ActivationFrequencies = countActivationFrequencies();
        ret += "#Activations\tFrequency\n";
        for(auto const& [nActivations, freq]: ActivationFrequencies)
            ret += std::to_string(nActivations) + "\t\t" + std::to_string(freq) + '\n';
        
        ret += "Modality\tFrequency\n";
        for(auto const& [m, freq]: ModalitiyFrequencies)
            ret += m.to_string() + "\t\t" + std::to_string(freq) + '\n';
        return ret;
    }

    std::vector<Activation> all_Activations() const
    {
        std::set<Activation> s;
        for(Neuron n: neurons) {
            for(Activation a: n.Activations)
                s.insert(a);
        }
        return std::vector<Activation>(s.begin(), s.end());
    }

    std::pair<Neuron&, Activation&> sampleActivation()
    {
        std::uniform_real_distribution<double> X(0, 1);
        double x = X(rd);
        unsigned nActivations = 0;
        for(auto n : neurons) {
            nActivations += n.Activations.size();
        }
        double prob = 0.0;
        for(auto& n : neurons){
            unsigned m = n.Activations.size();
            prob += double(m) / double(nActivations);
            if(x < prob) {
                std::uniform_int_distribution<unsigned> Y(0, m - 1);
                unsigned i = Y(rd);
                return std::pair<Neuron&, Activation&>(n, n.Activations[i]);
            }
        }
        assert(false);
    }

    void swap_in_place()
    {
        auto [n1, a1] = sampleActivation();
        auto [n2, a2] = sampleActivation();
        if(!n1.hasActivation(a2) && !n2.hasActivation(a1)) {
            n1.swap_Activation(a1, n2, a2);
        }
    }

    void testSwapping()
    {
        auto freq = frequencies_to_string();
        for(int i = 0; i < 10000; i++) {
            swap_in_place();
            auto new_freq = frequencies_to_string();
            if(new_freq != freq)
                assert(false);
            else
                freq = new_freq;
        }
    }


    unsigned int countExIn() {return countLoops<&Neuron::DownstreamFromExt, 
                                                &Neuron::DownstreamFromInh>();}
    unsigned int countInIn() {return countLoops<&Neuron::DownstreamFromInh,
                                                &Neuron::DownstreamFromInh>();}
    unsigned int countExEx() {return countLoops<&Neuron::DownstreamFromExt,
                                                &Neuron::DownstreamFromExt>();}



    void Loop_Swap_Statistics(unsigned n_reference_sets, std::string path)
    {
        auto stat = swap_statistics<NeuronSet, &NeuronSet::countExIn,
                                               &NeuronSet::countInIn,
                                               &NeuronSet::countExEx,
                                               &NeuronSet::count_unrecorded_feed_forward>
                                   (*this, n_reference_sets, n_threads);

        std::cout << stat.tidy_table<0>() << path << '\n';

        std::ofstream(path + "/ExIn.csv", std::ios::out) << stat.tidy_table<0>();
        std::ofstream(path + "/InIn.csv", std::ios::out) << stat.tidy_table<1>();
        std::ofstream(path + "/ExEx.csv", std::ios::out) << stat.tidy_table<2>();
        std::ofstream(path + "/FF.csv",   std::ios::out) << stat.tidy_table<3>();
    }




    /*Association Rule Analysis*/

    std::vector<rule<Activation>> all_rules() const
    {
        auto activations = all_Activations();
        std::vector<rule<Activation>> ret;
        
        for(auto a1: activations) {
            for(auto a2: activations)
                ret.push_back(rule(a1, a2));
        }
        
        return ret;
    }

    std::map<rule<Activation>, double> lhs_support
        (const std::vector<rule<Activation>> &rules) const
    {
        std::map<Activation, int> support;
        for(Neuron n: neurons) {
            for(Activation a: n.Activations)
                support[a]++;
        }
        std::map<rule<Activation>, double> ret;
        for(auto [lhs, rhs]: rules)
            ret[rule(lhs, rhs)] = double(support[lhs]) / double(neurons.size());
        return ret;
    }

    std::vector<double> confidence
        (const std::vector<rule<Activation>> &rules) const 
    {
        std::map<rule<Activation>, double> support = lhs_support(rules);
        std::map<rule<Activation>, unsigned> lhs_and_rhs;

        for(Neuron n: neurons) {
            for(auto a1: n.Activations) {
                for(auto a2: n.Activations)
                    lhs_and_rhs[rule(a1, a2)]++;
            }
        }
        std::vector<double> confidence;
        for(auto rule: rules) {
            double val = (double(lhs_and_rhs[rule]) / double(neurons.size())) / support[rule];
            confidence.push_back(val);
        }
        return confidence;
    }

    void Association_Rule_Swap_Analysis(unsigned n_reference_sets, std::string path)
    {
        auto rules = all_rules();

        auto stat = swap_statistics_dynamic<NeuronSet, rule<Activation>, double, &NeuronSet::confidence>
                                           (*this, n_reference_sets, rules, n_threads);

        std::ofstream(path + "/AssociationRules.csv", std::ios::out) << stat.tidy_table(rules);
    }
};

void find_good_example()
{
    NeuronSet s("../TidyData/tidyDataReduced.csv");

    Activation a("Ia", 1);
    Activation b("Ia", -2);
    rule<Activation> IaIa(a, b);
    double min_conf = 1.0;
    NeuronSet best_example = s;
    for(int n = 0; n < 100000; n++) {
        s.swap_in_place();
        auto rules = s.all_rules();
        auto conf = s.confidence(rules);
        int i = std::find(rules.begin(), rules.end(), IaIa) - rules.begin();
        if (conf[i] < min_conf) {
            min_conf = conf[i];
            best_example = s;
        }
    }
    std::cout << min_conf << '\n';
    std::cout << best_example.to_csv();
}

void generate_swap_examples()
{
    NeuronSet s("../Swap_Randomization_Illustration/Illustration_Data.csv");
    
    auto swap_10000 = [&s](){ for (int n = 0; n < 10000; n++) { s.swap_in_place(); } };

    swap_10000();

    for (int n = 0; n < 10; n++) {
        std::cout << s.to_csv() << '\n';
        swap_10000();
    }

}

void find_loops()
{
    NeuronSet s("../TidyData/tidyData.csv");

    s.countExEx();
    s.count_unrecorded_feed_forward();
    s.countExIn();
}

int main(int argc, const char *argv[])
{
    std::string data, output, analysis_type;

    po::options_description desc{"Options"};
    desc.add_options()
        ("help", "Print this screen")
        ("data",     po::value<std::string>(&data),          "Path to dataset")
        ("output",   po::value<std::string>(&output),        "Path to folder where to write results")
        ("analysis", po::value<std::string>(&analysis_type), "Type of analyis [loop|association]");

    try {
        po::command_line_parser parser{argc, argv};
        parser.options(desc).allow_unregistered().style(
            po::command_line_style::default_style |
            po::command_line_style::allow_slash_for_short);
        po::parsed_options parsed_options = parser.run();

        po::variables_map vm;
        store(parsed_options, vm);
        notify(vm);

        if (!vm.count("data") || !vm.count("analysis") || !vm.count("output")) {
            std::cerr << "Provide a dataset an analysis type and an output directory\n";
            std::cerr << '\n' << desc << '\n';
            return 1;
        }

        if (analysis_type != "loop" && analysis_type != "association") {
            std::cerr << "Analysis type must be either loop or association\n";
            std::cerr << "You provided \"" << analysis_type << '\"'<< '\n';
            return 1;
        }
    } catch (const po::error &ex) {
        std::cerr << "Caught " << ex.what() << '\n';
        std::cout << '\n' << desc << '\n';
        return 1;
    }

    try {
        NeuronSet s(data);
        unsigned n_reference_sets = 10000000;

        if(analysis_type == "loop") {
            std::cout << "Computing swap statistics of loops for " << data << '\n';
            s.Loop_Swap_Statistics(n_reference_sets, output);
        } else if(analysis_type == "association") {
            std::cout << "Computing swap statistics of association rules for " << data << '\n';
            s.Association_Rule_Swap_Analysis(n_reference_sets, output);
        }
    } catch (const std::exception &e) {
        std::cerr << "Caught " << e.what() << '\n';
        return 1;
    }
 
    return 0;
}
