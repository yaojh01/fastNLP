
from fastNLP.core.instance import Instance
from fastNLP.core.dataset import DataSet
from fastNLP.api.pipeline import Pipeline
from fastNLP.api.processor import FullSpaceToHalfSpaceProcessor
from fastNLP.api.processor import IndexerProcessor
from reproduction.chinese_word_segment.process.cws_processor import SpeicalSpanProcessor
from reproduction.chinese_word_segment.process.cws_processor import CWSCharSegProcessor
from reproduction.chinese_word_segment.process.cws_processor import CWSSegAppTagProcessor
from reproduction.chinese_word_segment.process.cws_processor import Pre2Post2BigramProcessor
from reproduction.chinese_word_segment.process.cws_processor import VocabProcessor

from reproduction.chinese_word_segment.process.span_converter import AlphaSpanConverter
from reproduction.chinese_word_segment.process.span_converter import DigitSpanConverter
from reproduction.chinese_word_segment.io.cws_reader import NaiveCWSReader
from reproduction.chinese_word_segment.models.cws_model import CWSBiLSTMSegApp

tr_filename = ''
dev_filename = ''

reader = NaiveCWSReader()

tr_sentences = reader.load(tr_filename, cut_long_sent=True)
dev_sentences = reader.load(dev_filename)


# TODO 如何组建成为一个Dataset
def construct_dataset(sentences):
    dataset = DataSet()
    for sentence in sentences:
        instance = Instance()
        instance['raw_sentence'] = sentence
        dataset.append(instance)

    return dataset


tr_dataset = construct_dataset(tr_sentences)
dev_dataset = construct_dataset(dev_sentences)

# 1. 准备processor
fs2hs_proc = FullSpaceToHalfSpaceProcessor('raw_sentence')

sp_proc = SpeicalSpanProcessor('raw_sentence', 'sentence')
sp_proc.add_span_converter(AlphaSpanConverter())
sp_proc.add_span_converter(DigitSpanConverter())

char_proc = CWSCharSegProcessor('sentence', 'char_list')

tag_proc = CWSSegAppTagProcessor('sentence', 'tag')

bigram_proc = Pre2Post2BigramProcessor('char_list', 'bigram_list')

char_vocab_proc = VocabProcessor('char_list')
bigram_vocab_proc = VocabProcessor('bigram_list')

# 2. 使用processor
fs2hs_proc(tr_dataset)

sp_proc(tr_dataset)

char_proc(tr_dataset)
tag_proc(tr_dataset)
bigram_proc(tr_dataset)

char_vocab_proc(tr_dataset)
bigram_vocab_proc(tr_dataset)

char_index_proc = IndexerProcessor(char_vocab_proc.get_vocab(), 'chars_list', 'indexed_chars_list')
bigram_index_proc = IndexerProcessor(bigram_vocab_proc.get_vocab(), 'bigrams_list','indexed_bigrams_list')

char_index_proc(tr_dataset)
bigram_index_proc(tr_dataset)

# 2.1 处理dev_dataset
fs2hs_proc(dev_dataset)

sp_proc(dev_dataset)

char_proc(dev_dataset)
tag_proc(dev_dataset)
bigram_proc(dev_dataset)

char_index_proc(dev_dataset)
bigram_index_proc(dev_dataset)


# 3. 得到数据集可以用于训练了
# TODO pretrain的embedding是怎么解决的？
cws_model = CWSBiLSTMSegApp(vocab_num, embed_dim=100, bigram_vocab_num=None, bigram_embed_dim=100, num_bigram_per_char=None,
                 hidden_size=200, bidirectional=True, embed_drop_p=None, num_layers=1, tag_size=2)




# 4. 组装需要存下的内容
pp = Pipeline()
pp.add_processor(fs2hs_proc)
pp.add_processor(sp_proc)
pp.add_processor(char_proc)
pp.add_processor(bigram_proc)
pp.add_processor(char_index_proc)
pp.add_processor(bigram_index_proc)