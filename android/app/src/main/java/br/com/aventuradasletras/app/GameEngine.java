package br.com.aventuradasletras.app;

import java.text.Normalizer;
import java.util.*;

/** Platform-independent rules, shared by the native UI and JVM smoke tests. */
public final class GameEngine {
    public static final class Word {
        public final String word, category, image, clue, audio;
        public final int level;
        public Word(String word, int level, String category, String image, String clue, String audio) {
            this.word=word; this.level=level; this.category=category; this.image=image; this.clue=clue; this.audio=audio;
        }
    }
    public final List<Word> words;
    public final Set<String> seen = new HashSet<>();
    public final Set<String> chosen = new HashSet<>();
    public final Set<String> highlighted = new HashSet<>();
    public Word current;
    public int level=1, mistakes=0, helpStage=0;
    public boolean assisted=false, completed=false, picture=false;
    public Set<String> categories = new HashSet<>(Arrays.asList("animais","alimentos","brinquedos","casa","natureza"));
    private final Random random;
    private List<String> keys=new ArrayList<>();
    public GameEngine(List<Word> words) { this(words, new Random()); }
    public GameEngine(List<Word> words, Random random) { this.words=words; this.random=random; }
    public static String base(String text) {
        // Ç is a distinct key. Accents on vowels are revealed by their base letter.
        return Normalizer.normalize(text.toUpperCase(Locale.ROOT).replace("Ç","\u0001"),Normalizer.Form.NFD)
            .replaceAll("\\p{M}","").replace("\u0001","Ç");
    }
    public List<Word> pool() {
        List<Word> list=new ArrayList<>();
        for(Word w:words) if(w.level==level && categories.contains(w.category)) list.add(w);
        return list;
    }
    public boolean next() {
        List<Word> available=pool();
        Iterator<Word> iterator=available.iterator();
        while(iterator.hasNext()) if(seen.contains(iterator.next().word))iterator.remove();
        if(available.isEmpty()) { current=null; return false; }
        current=available.get(random.nextInt(available.size()));
        seen.add(current.word); chosen.clear(); highlighted.clear();
        mistakes=0; helpStage=0; assisted=false; completed=false; picture=level!=3;
        Set<String> letters=new LinkedHashSet<>();
        for(char c:base(current.word).toCharArray()) letters.add(String.valueOf(c));
        if(level==1) {
            List<String> distractors=new ArrayList<>();
            for(char c='A';c<='Z';c++) if(!letters.contains(String.valueOf(c))) distractors.add(String.valueOf(c));
            Collections.shuffle(distractors,random);
            for(String s:distractors) { if(letters.size()>=8) break; letters.add(s); }
        } else {
            for(char c='A';c<='Z';c++) letters.add(String.valueOf(c));
            if(base(current.word).contains("Ç")) letters.add("Ç");
        }
        keys=new ArrayList<>(letters); Collections.sort(keys);
        return true;
    }
    public void restartSequence() { for(Word w:pool()) seen.remove(w.word); next(); }
    public List<String> keys() { return keys; }
    public boolean contains(String letter) { return current!=null && base(current.word).contains(letter); }
    public boolean guess(String raw) {
        String letter=base(raw);
        if(current==null || completed || !keys.contains(letter) || chosen.contains(letter)) return false;
        chosen.add(letter); highlighted.remove(letter);
        if(!contains(letter)) mistakes++;
        completed=true;
        for(char c:base(current.word).toCharArray()) if(!chosen.contains(String.valueOf(c))) completed=false;
        return true;
    }
    public boolean visible(int index) { return chosen.contains(base(current.word.substring(index,index+1))); }
    public List<String> missing() {
        List<String> missing=new ArrayList<>();
        for(char c:base(current.word).toCharArray()) {
            String s=String.valueOf(c);
            if(!chosen.contains(s) && !missing.contains(s)) missing.add(s);
        }
        return missing;
    }
    public void highlight() {
        if(current==null || completed) return;
        assisted=true; highlighted.clear();
        List<String> missing=missing();
        if(!missing.isEmpty()) highlighted.add(missing.get(0));
        for(String k:keys) if(!chosen.contains(k) && !contains(k)) { highlighted.add(k); if(highlighted.size()>=3) break; }
    }
    public void reveal() {
        if(current==null || completed) return;
        assisted=true;
        List<String> missing=missing();
        if(!missing.isEmpty()) guess(missing.get(0));
    }
}
