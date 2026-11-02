import br.com.aventuradasletras.app.GameEngine;
import java.util.*;

public class GameEngineTest {
    static int checks=0;
    static void check(boolean condition, String description) { checks++; if(!condition)throw new AssertionError(description); }
    static GameEngine.Word word(String text,int level) { return new GameEngine.Word(text,level,"alimentos","image.png","Pista","Áudio"); }
    public static void main(String[] args) {
        GameEngine game=new GameEngine(Arrays.asList(word("OVO",1)),new Random(3));
        check(game.next(),"round starts");
        check(game.keys().size()==8,"eight beginner options");
        check(game.keys().containsAll(Arrays.asList("O","V")),"all necessary letters");
        check(game.guess("O"),"first guess accepted");
        check(game.visible(0)&&game.visible(2),"all repeated occurrences revealed");
        check(!game.guess("O"),"duplicate rejected");
        game.guess("V"); check(game.completed,"word complete");
        check(!game.next(),"no repetition until sequence exhausted");
        game.restartSequence(); check(game.current!=null,"explicit restart");
        game.highlight(); check(game.assisted,"help recorded");
        while(!game.completed)game.reveal(); check(game.completed,"assisted completion");
        check(GameEngine.base("MAÇÃ").equals("MAÇA"),"accents normalized and Ç preserved");
        GameEngine accent=new GameEngine(Arrays.asList(word("MAÇÃ",2))); accent.level=2; accent.next();
        check(accent.keys().contains("Ç"),"separate Ç key"); accent.guess("A");
        check(accent.visible(1)&&accent.visible(3),"base letter reveals accented vowel");
        GameEngine filtered=new GameEngine(Arrays.asList(word("OVO",1),new GameEngine.Word("GATO",1,"animais","x","x","x")));
        filtered.categories=new HashSet<>(Arrays.asList("animais")); filtered.next(); check(filtered.current.word.equals("GATO"),"category filter");
        System.out.println("Native game rules: "+checks+" checks passed.");
    }
}
