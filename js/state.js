// グローバル状態・定数・t()
const BASE = '';
const TARGET_CATS = [1, 5, 6, 7];
const DISPLAY_LIMIT = 20;

let vocab      = [];
let lineData   = [];
let popTarget  = null;
let sortBy     = 'freq';  // 'freq' | 'id'
let catFilter  = 0;       // 0=全て -1=対象外 1/5/6/7=指定カテゴリ
function t(key, ...args) {
  const val = LOCALES['en-ja'][key];
  return typeof val === 'function' ? val(...args) : (val ?? key);
}

const STOP_WORDS = new Set([
  'a','an','the','is','are','was','were','be','been','being','have','has',
  'had','do','does','did','will','would','could','should','may','might',
  'shall','can','to','of','in','on','at','by','for','with','as','from',
  'this','that','these','those','it','its','and','or','but','not','if',
  'then','when','where','how','what','which','who','so','yet','no','nor',
  'all','any','each','few','more','most','other','some','such','up','out',
  'about','after','before','into','through','during','without','between',
  'i','we','you','he','she','they','my','your','his','her','our','their',
  'me','him','us','them','new','get','use','see','now','here','there','set',
  'also','just','than','too','very','only','both','already','still','well'
]);
