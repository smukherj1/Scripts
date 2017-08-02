#include <iostream>
#include <functional>
#include <iterator>
#include <string>
#include <utility>
#include <type_traits>

namespace detail
{
template <class BidirIterator,
          class Equals>
class LongestPalindromeImpl
{
    static_assert(
        std::is_base_of<std::bidirectional_iterator_tag, typename std::iterator_traits<BidirIterator>::iterator_category>::value,
        "LongestPalindromeImpl requires a bidirectional iterator");

    bool is_palindrome(BidirIterator start, BidirIterator end)
    {
        auto result = true;
        for ( ;(start != end) && ((end + 1) != start); ++start, --end)
        {
            if (!m_equality_checker(*start, *end))
            {
                return false;
            }
        }
        return result;
    }

  public:
    LongestPalindromeImpl(BidirIterator begin, BidirIterator end) : m_begin(begin),
                                                                    m_end(end)
    {
    }

    auto get()
    {
        for (auto start_it = m_begin; start_it != m_end; ++start_it)
        {
            for (auto end_it = m_end - 1; end_it != m_begin; --end_it)
            {
                if(is_palindrome(start_it, end_it)) {
                    return std::make_pair(start_it, end_it + 1);
                }
            }
        }
        return std::make_pair(m_end, m_end);
    }

  private:
    Equals m_equality_checker;
    BidirIterator m_begin;
    BidirIterator m_end;
};

template <class BidirIterator,
          class Equals = std::equal_to<typename std::iterator_traits<BidirIterator>::value_type>>
LongestPalindromeImpl<BidirIterator, Equals> make_longest_palindrome_impl(BidirIterator begin, BidirIterator end)
{
    return LongestPalindromeImpl<BidirIterator, Equals>(begin, end);
}
}

auto longest_palindrome(const std::string &input)
{
    auto longest_range_pair = detail::make_longest_palindrome_impl(input.begin(), input.end()).get();
    return std::string(longest_range_pair.first, longest_range_pair.second);
}

int main()
{
    std::string seq1 = "abba";
    std::string seq2 = "cabbd";

    std::cout << seq1 << ", " << longest_palindrome(seq1) << "\n";
    std::cout << seq2 << ", " << longest_palindrome(seq2) << "\n";

    return 0;
}
