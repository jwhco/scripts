/**
 * Automatically remove stop words and low-value keywords when an automatic permalink is first suggested by WordPress
 */
 
function remove_stop_words_permalink($post_id) {
        if (wp_is_post_revision($post_id) || (defined('DOING_AUTOSAVE') && DOING_AUTOSAVE)) {
                return;
        }
        // Optimize stop words lookup using array_flip for faster lookups
        $common_keywords = array_flip(array(
                "a", "about", "above", "after", "again", "against", "aint", "all", "am", "an", "and", "any", "are", "arent", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can", "cannot", "cant", "could", "couldnt", "did", "didnt", "do", "does", "doesnt", "doing", "dont", "down", "during", "each", "few", "for", "from", "further", "had", "hadnt", "has", "hasnt", "have", "havent", "having", "he", "hed", "hell", "her", "here", "heres", "hers", "herself", "hes", "him", "himself", "his", "how", "hows", "i", "id", "if", "ill", "im", "in", "into", "is", "isnt", "it", "its", "itself", "ive", "lets", "me", "mightnt", "more", "most", "mustnt", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "shant", "she", "shed", "shell", "shes", "should", "shouldnt", "so", "some", "such", "than", "that", "thats", "the", "their", "theirs", "them", "themselves", "then", "there", "theres", "these", "they", "theyd", "theyll", "theyre", "theyve", "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasnt", "we", "wed", "well", "were", "werent", "weve", "what", "whats", "when", "whens", "where", "wheres", "which", "while", "who", "whom", "whos", "why", "whys", "with", "wont", "would", "wouldnt", "you", "youd", "youll", "your", "youre", "yours", "yourself", "yourselves", "youve"
        ));
        $post_title = get_post_field('post_title', $post_id);
        $title_words = explode(' ', $post_title);
        $filtered_title = array_filter($title_words, function($word) use($common_keywords) {
                $lower_word = strtolower($word); // Cache strtolower result
                return !isset($common_keywords[$lower_word]);
        });
        $clean_title = implode(' ', $filtered_title);
        $new_slug = sanitize_title($clean_title);
        remove_action('save_post', 'remove_stop_words_permalink');
        wp_update_post(array('ID' => $post_id, 'post_name' => $new_slug));
        add_action('save_post', 'remove_stop_words_permalink');
}
add_action('save_post', 'remove_stop_words_permalink');