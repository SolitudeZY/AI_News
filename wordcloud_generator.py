import os
import re
import json
import jieba
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
import re
import math
from typing import List, Dict, Tuple
import time
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # 设置中文字体
matplotlib.rcParams['axes.unicode_minus'] = False  # 正常显示负号

class WordCloudGenerator:
    def __init__(self, width=800, height=400, background_color='white', max_words=100, 
                 tfidf_threshold=0.1, top_n_words=100, enable_cache=True):
        self.width = width
        self.height = height
        self.background_color = background_color
        self.max_words = max_words
        self.tfidf_threshold = tfidf_threshold
        self.top_n_words = top_n_words
        self.enable_cache = enable_cache
        self.cache = {}
        # Use a font that supports Chinese, default to SimHei
        self.font_path = 'C:/Windows/Fonts/simhei.ttf'  # Common path for Windows
        # If font not found, wordcloud will use default, but might not support Chinese well
        if not os.path.exists(self.font_path):
            self.font_path = None  # Let wordcloud use default font

    def preprocess_text(self, text, return_tokens=False):
        """Preprocess text: remove punctuation, segment Chinese text, and filter stopwords"""
        # Remove HTML tags
        text = re.sub(r'<.*?>', '', text)
        # Remove URLs
        text = re.sub(r'http[s]?://\\S+', '', text)
        # Remove punctuation and numbers
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\d+', '', text)
        
        # Load Chinese stopwords from file
        stopwords_file = 'chinese_stopwords.txt'
        chinese_stopwords = set()
        if os.path.exists(stopwords_file):
            with open(stopwords_file, 'r', encoding='utf-8') as f:
                chinese_stopwords = set(line.strip() for line in f if line.strip())
        else:
            # Fallback to default stopwords if file not found
            chinese_stopwords = {'的', '地', '得', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这', '那', '他', '她', '它', '我们', '你们', '他们', '这个', '那个', '这些', '那些', '这样', '那样', '什么', '怎么', '为什么', '因为', '所以', '但是', '然后', '如果', '虽然', '可以', '应该', '能够', '已经', '还是', '或者', '而且', '为了', '关于', '通过', '根据', '按照', '由于', '对于', '作为', '就是'}
        
        # Segment Chinese text using jieba and filter stopwords
        words = list(jieba.cut(text))
        # Debug print
        # print(f"Jieba cut words: {words[:10]}") # Print first 10 words
        filtered_words = [word for word in words if word not in chinese_stopwords and len(word) > 1]
        # Debug print
        # print(f"Filtered words: {filtered_words[:10]}") # Print first 10 filtered words
        
        if return_tokens:
            return filtered_words
        return ' '.join(filtered_words)

    def calculate_tfidf(self, documents: List[str], progress_callback=None) -> Dict[str, float]:
        """Calculate TF-IDF values for words across documents"""
        if self.enable_cache:
            cache_key = hash(tuple(documents))
            if cache_key in self.cache:
                return self.cache[cache_key]
        
        total_docs = len(documents)
        word_doc_freq = Counter()
        doc_word_freqs = []
        
        # Preprocess each document and count word frequencies
        for i, doc in enumerate(documents):
            if progress_callback:
                progress_callback(f"Processing document {i+1}/{total_docs}", i/total_docs)
            
            tokens = self.preprocess_text(doc, return_tokens=True)
            word_freq = Counter(tokens)
            doc_word_freqs.append(word_freq)
            
            # Update document frequency for unique words in this document
            for word in set(tokens):
                word_doc_freq[word] += 1
        
        # Calculate TF-IDF for each word
        tfidf_scores = {}
        for i, word_freq in enumerate(doc_word_freqs):
            if progress_callback:
                progress_callback(f"Calculating TF-IDF for document {i+1}/{total_docs}", (i + 0.5)/total_docs)
            
            total_words = sum(word_freq.values())
            for word, freq in word_freq.items():
                # Term Frequency (TF)
                tf = freq / total_words
                # Inverse Document Frequency (IDF)
                if word_doc_freq[word] == total_docs:
                    idf = 0  # Word appears in all documents, so it's not discriminative
                else:
                    idf = math.log(total_docs / word_doc_freq[word])
                # TF-IDF
                tfidf = tf * idf

                # Debug print for TF-IDF calculation
                # if word in ["人工智能", "机器学习"]:
                #     print(f"Debug TF-IDF for '{word}': tf={tf:.4f}, idf={idf:.4f}, tfidf={tfidf:.4f}, total_docs={total_docs}, word_doc_freq={word_doc_freq[word]}")
                
                if word not in tfidf_scores or tfidf > tfidf_scores[word]:
                    tfidf_scores[word] = tfidf
        
        # Filter by threshold and sort
        filtered_scores = {word: score for word, score in tfidf_scores.items() 
                          if score >= self.tfidf_threshold}
        sorted_scores = dict(sorted(filtered_scores.items(), key=lambda x: x[1], reverse=True)[:self.top_n_words])
        
        if self.enable_cache:
            self.cache[cache_key] = sorted_scores
        
        if progress_callback:
            progress_callback("TF-IDF calculation completed", 1.0)
        
        return sorted_scores

    def generate_tfidf_wordcloud(self, articles, output_path='wordcloud.png', progress_callback=None):
        """Generate word cloud using TF-IDF weights"""
        # Extract text from articles
        documents = []
        for article in articles:
            title = article.get('title', '')
            description = article.get('description', '')
            documents.append(title + ' ' + description)
        
        if not any(doc.strip() for doc in documents):
            raise ValueError("No text content to generate word cloud")
        
        # Calculate TF-IDF scores
        tfidf_scores = self.calculate_tfidf(documents, progress_callback)
        
        if not tfidf_scores:
            raise ValueError("No words passed TF-IDF threshold")
        
        # Create frequency dictionary for wordcloud (using TF-IDF as weight)
        word_freq = tfidf_scores
        
        # Generate word cloud
        wordcloud = WordCloud(
            width=self.width,
            height=self.height,
            background_color=self.background_color,
            max_words=self.max_words,
            font_path=self.font_path,
            relative_scaling=0.5  # Better scaling for TF-IDF values
        ).generate_from_frequencies(word_freq)
        
        # Save the image
        wordcloud.to_file(output_path)
        
        # Generate legend and save data
        self._generate_legend(tfidf_scores, output_path.replace('.png', '_legend.png'))
        self._export_tfidf_data(tfidf_scores, output_path.replace('.png', '_data.csv'))
        
        return output_path, tfidf_scores

    def _generate_legend(self, tfidf_scores: Dict[str, float], legend_path: str):
        """Generate a legend showing TF-IDF value ranges"""
        if not tfidf_scores:
            return
        
        values = list(tfidf_scores.values())
        min_val, max_val = min(values), max(values)
        
        fig = plt.figure(figsize=(10, 8)) # Keep height for better spacing
        
        # Define positions for colorbar and words axes
        # [left, bottom, width, height] in figure coordinates (0 to 1)
        cbar_ax_pos = [0.1, 0.78, 0.8, 0.03] # Colorbar at the top, thinner, slightly lower bottom
        words_ax_pos = [0.1, 0.08, 0.8, 0.6] # Words below, taking most of the space, adjusted height and higher bottom
        
        # Create axis for colorbar
        ax_cbar = fig.add_axes(cbar_ax_pos)
        ax_cbar.set_xticks([]) 
        ax_cbar.set_yticks([]) 
        ax_cbar.spines['top'].set_visible(False) 
        ax_cbar.spines['right'].set_visible(False)
        ax_cbar.spines['bottom'].set_visible(False)
        ax_cbar.spines['left'].set_visible(False)

        # Create color gradient
        cmap = plt.cm.viridis
        norm = plt.Normalize(min_val, max_val)
        
        # Create colorbar
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        
        cbar = plt.colorbar(sm, cax=ax_cbar, orientation='horizontal') # Use cax for direct axis control
        cbar.set_label('TF-IDF Value', fontsize=12, fontweight='bold', labelpad=10) # Decrease labelpad to move label closer to colorbar
        cbar.ax.tick_params(labelsize=10)
        
        # Create axis for top words
        ax_words = fig.add_axes(words_ax_pos)
        ax_words.axis('off') # Hide axis for words section
        
        # Add title for words section
        # Position it relative to the words_ax_pos, slightly above the word boxes
        ax_words.text(0.5, 1.02, 'Top Words by TF-IDF Score', # Adjust y position
                     transform=ax_words.transAxes, 
                     fontsize=14, # Slightly larger title
                     fontweight='bold',
                     ha='center',
                     va='top') # Align to top of the text box
        
        # Add top words with better formatting
        top_words = list(tfidf_scores.items())[:8]  # Show more words
        
        # Create a table-like display for top words
        # Adjust y_pos to start below the title
        y_start_text = 0.9 # Start position for the first word text, relative to ax_words
        box_height = 0.08 # Height of each word entry box
        spacing = 0.02 # Spacing between boxes
        
        for i, (word, score) in enumerate(top_words):
            # Calculate y position for the center of the text
            text_y_center = y_start_text - i * (box_height + spacing)
            
            # Calculate bottom-left corner for the rectangle
            rect_bottom = text_y_center - box_height / 2
            
            # Create a colored box for each word
            color = cmap(norm(score))
            rect = plt.Rectangle((0.1, rect_bottom), 0.8, box_height, # Adjust rect position and height
                               facecolor=color, alpha=0.7, transform=ax_words.transAxes)
            ax_words.add_patch(rect)
            
            # Add word text
            ax_words.text(0.15, text_y_center, f"{word}", 
                         transform=ax_words.transAxes, 
                         fontsize=11, 
                         fontweight='bold',
                         va='center',
                         ha='left',
                         color='white' if score > (min_val + max_val)/2 else 'black')
            
            # Add score text
            ax_words.text(0.85, text_y_center, f"{score:.4f}", 
                         transform=ax_words.transAxes, 
                         fontsize=10, 
                         va='center',
                         ha='right',
                         color='white' if score > (min_val + max_val)/2 else 'black')
            
        plt.savefig(legend_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()

    def _export_tfidf_data(self, tfidf_scores: Dict[str, float], data_path: str):
        """Export TF-IDF data to CSV file"""
        with open(data_path, 'w', encoding='utf-8') as f:
            f.write("Word,TF-IDF_Score\n")
            for word, score in sorted(tfidf_scores.items(), key=lambda x: x[1], reverse=True):
                f.write(f'"{word}",{score:.6f}\n')

    def generate_wordcloud(self, articles, output_path='wordcloud.png', use_tfidf=False, progress_callback=None):
        """Generate word cloud from list of articles"""
        if use_tfidf:
            return self.generate_tfidf_wordcloud(articles, output_path, progress_callback)
        
        # Original method for backward compatibility
        # Combine all titles and descriptions
        all_text = ''
        for article in articles:
            title = article.get('title', '')
            description = article.get('description', '')
            all_text += title + ' ' + description + ' '

        if not all_text.strip():
            raise ValueError("No text content to generate word cloud")

        # Preprocess the text
        processed_text = self.preprocess_text(all_text)

        # Generate word cloud
        wordcloud = WordCloud(
            width=self.width,
            height=self.height,
            background_color=self.background_color,
            max_words=self.max_words,
            font_path=self.font_path
        ).generate(processed_text)

        # Save the image
        wordcloud.to_file(output_path)
        return output_path

    def generate_from_json(self, json_filename, output_path='wordcloud.png'):
        """Generate word cloud from JSON data (like news_data.json)"""
        try:
            with open(json_filename, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            articles = json_data.get('news', [])
            return self.generate_wordcloud(articles, output_path)
        except Exception as e:
            print(f"Error loading JSON file {json_filename}: {e}")
            return None