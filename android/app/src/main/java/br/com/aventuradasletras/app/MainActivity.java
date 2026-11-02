package br.com.aventuradasletras.app;

import android.app.*;
import android.os.*;
import android.content.*;
import android.graphics.*;
import android.graphics.drawable.*;
import android.speech.tts.*;
import android.view.*;
import android.widget.*;
import org.json.*;
import java.io.*;
import java.util.*;

/** Genuine native Android application: views, local assets, local preferences and Android TTS. */
public class MainActivity extends Activity {
    private static final int INK=Color.rgb(35,63,52), GREEN=Color.rgb(51,104,82), CREAM=Color.rgb(248,247,238), GOLD=Color.rgb(246,215,145);
    private static final String[] LEVELS={"Primeiros passos","Descobrindo letras","Novo desafio"};
    private static final String[] CATEGORIES={"animais","alimentos","brinquedos","casa","natureza"};
    private static final String[] CAT_NAMES={"Animais","Alimentos","Brinquedos","Objetos de casa","Natureza"};
    private GameEngine engine;
    private android.content.SharedPreferences prefs;
    private JSONObject history;
    private TextToSpeech tts;
    private boolean voiceReady=false, audio=true, hints=true, reduced=false, started=false;
    private LinearLayout page, slots, keyboard;
    private TextView feedback, progress;
    private Button helpButton, nextButton, soundButton, imageButton;
    private ImageView image;
    private final Handler handler=new Handler(Looper.getMainLooper());
    private final Map<String,Button> keyViews=new HashMap<>();
    private String message="Toque em uma letra para descobrir a palavra.";
    private boolean celebrationRecorded=false;
    private final List<Runnable> animationTasks=new ArrayList<>();

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        prefs=getSharedPreferences("aventura-das-letras",MODE_PRIVATE);
        audio=prefs.getBoolean("audio",true); hints=prefs.getBoolean("hints",true); reduced=prefs.getBoolean("reduced",false);
        try {
            history=new JSONObject(prefs.getString("history","{}"));
            JSONArray data=new JSONArray(readAsset("content/words.json"));
            List<GameEngine.Word> words=new ArrayList<>();
            for(int i=0;i<data.length();i++) {
                JSONObject o=data.getJSONObject(i);
                words.add(new GameEngine.Word(o.getString("word"),o.getInt("level"),o.getString("category"),o.getString("image"),o.getString("clue"),o.getString("audio")));
            }
            engine=new GameEngine(words); engine.level=prefs.getInt("level",1);
            engine.categories=new HashSet<>(prefs.getStringSet("categories",new HashSet<>(Arrays.asList(CATEGORIES))));
            if(engine.categories.isEmpty()) engine.categories.addAll(Arrays.asList(CATEGORIES));
        } catch(Exception e) { fatal("Não foi possível abrir o conteúdo do jogo. Reinstale o aplicativo."); return; }
        tts=new TextToSpeech(this,status -> {
            if(status==TextToSpeech.SUCCESS) {
                tts.setLanguage(new Locale("pt","BR"));
                Set<Voice> voices=tts.getVoices();
                if(voices!=null) for(Voice voice:voices) {
                    if("pt".equals(voice.getLocale().getLanguage()) && "BR".equals(voice.getLocale().getCountry()) && !voice.isNetworkConnectionRequired() && (voice.getFeatures()==null || !voice.getFeatures().contains(TextToSpeech.Engine.KEY_FEATURE_NOT_INSTALLED))) {
                        tts.setVoice(voice); voiceReady=true; break;
                    }
                }
                tts.setSpeechRate(0.82f);
                if(started && engine.current!=null && engine.level==1) speak(engine.current.audio);
            }
        });
        showWelcome();
    }
    private String readAsset(String path) throws IOException {
        try(InputStream in=getAssets().open(path); ByteArrayOutputStream out=new ByteArrayOutputStream()) {
            byte[] b=new byte[4096]; int count;
            while((count=in.read(b))!=-1) out.write(b,0,count);
            return out.toString("UTF-8");
        }
    }
    private void fatal(String text) { TextView t=label(text,20); t.setPadding(dp(24),dp(60),dp(24),dp(24)); setContentView(t); }
    private int dp(float n) { return (int)(getResources().getDisplayMetrics().density*n+0.5f); }
    private GradientDrawable background(int color,int radius) {
        GradientDrawable d=new GradientDrawable(); d.setColor(color); d.setCornerRadius(dp(radius)); return d;
    }
    private TextView label(String text,int size) {
        TextView v=new TextView(this); v.setText(text); v.setTextSize(size); v.setTextColor(INK); v.setGravity(Gravity.CENTER_VERTICAL); v.setFontFeatureSettings("kern"); return v;
    }
    private TextView title(String text,int size) { TextView t=label(text,size); t.setTypeface(null,android.graphics.Typeface.BOLD); return t; }
    private LinearLayout column() { LinearLayout l=new LinearLayout(this); l.setOrientation(LinearLayout.VERTICAL); return l; }
    private LinearLayout row() { LinearLayout l=new LinearLayout(this); l.setOrientation(LinearLayout.HORIZONTAL); l.setGravity(Gravity.CENTER_VERTICAL); return l; }
    private void add(LinearLayout parent,View child,int height,int margin) {
        LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(-1,height<0?height:dp(height)); p.setMargins(0,dp(margin),0,0); parent.addView(child,p);
    }
    private Button button(String text,boolean primary,Runnable action) {
        Button b=new Button(this); b.setText(text); b.setAllCaps(false); b.setTextSize(15); b.setTypeface(null,android.graphics.Typeface.BOLD);
        b.setTextColor(primary?Color.WHITE:INK); b.setBackground(background(primary?GREEN:Color.rgb(235,238,225),16));
        b.setPadding(dp(10),dp(8),dp(10),dp(8)); b.setMinHeight(dp(50)); b.setOnClickListener(v -> action.run()); return b;
    }
    private void basePage() {
        clearAnimations();
        ScrollView scroll=new ScrollView(this); scroll.setFillViewport(true); scroll.setBackgroundColor(CREAM);
        page=column(); page.setPadding(dp(18),dp(12),dp(18),dp(24)); scroll.addView(page,new ScrollView.LayoutParams(-1,-2));
        scroll.setOnApplyWindowInsetsListener((v,insets) -> {
            v.setPadding(insets.getSystemWindowInsetLeft(),insets.getSystemWindowInsetTop(),insets.getSystemWindowInsetRight(),insets.getSystemWindowInsetBottom()); return insets;
        });
        setContentView(scroll);
        LinearLayout top=row(); TextView brand=title("✿  AVENTURA DAS LETRAS",13);
        top.addView(brand,new LinearLayout.LayoutParams(0,-2,1));
        Button parents=button("Responsáveis",false,this::showParents); parents.setTextSize(12); top.addView(parents,new LinearLayout.LayoutParams(dp(120),dp(46))); add(page,top,-2,0);
    }
    private void showWelcome() {
        basePage();
        add(page,title("Um jardim de\ndescobertas.",36),-2,28);
        TextView intro=label("Descubra a Palavra\nUma aventura para aprender no seu ritmo.",18); add(page,intro,-2,12);
        add(page,new GardenView(this),200,12);
        TextView description=label("Veja a imagem, ouça a palavra e toque nas letras. A Lili, sua amiga do jardim, ajuda você!",18); description.setLineSpacing(dp(4),1); add(page,description,-2,12);
        add(page,button("▶  Vamos brincar",true,() -> { started=true; nextRound(); }),56,22);
        Button instructions=button(audio?"♫  Ouvir instruções":"♫  Som desligado",false,() -> speak("Vamos brincar! Veja a imagem e toque nas letras. Você pode ouvir a palavra ou pedir uma ajudinha. Não precisa ter pressa.")); instructions.setEnabled(audio); add(page,instructions,52,10);
        add(page,label("Sem pressa. Cada descoberta floresce.",13),-2,16);
    }
    private void nextRound() {
        if(tts!=null) tts.stop();
        if(!engine.next()) { showSequenceEnd(); return; }
        celebrationRecorded=false; message="Toque em uma letra. Vamos descobrir juntos!";
        record(false); showGame();
        if(engine.level==1) speak(engine.current.audio);
    }
    private void showSequenceEnd() {
        basePage(); add(page,new GardenView(this),160,20);
        add(page,title("Seu jardim floresceu!",28),-2,16);
        add(page,label(engine.pool().isEmpty()?"Não há palavras nesta combinação. Escolha outras categorias na área dos responsáveis.":"Você praticou todas as palavras desta seleção. Quer descobrir tudo de novo?",18),-2,16);
        if(!engine.pool().isEmpty()) add(page,button("↻  Nova sequência",true,() -> { engine.restartSequence(); celebrationRecorded=false; record(false); showGame(); if(engine.level==1)speak(engine.current.audio); }),56,24);
        add(page,button("⚙  Escolher nível e categorias",false,this::showParents),56,12);
    }
    private void showGame() {
        basePage(); keyViews.clear(); imageButton=null;
        if(engine.current==null) { showSequenceEnd(); return; }
        LinearLayout meta=row(); TextView level=title(LEVELS[engine.level-1],14); meta.addView(level,new LinearLayout.LayoutParams(0,-2,1));
        progress=label("✿ "+completedCount()+" descobertas",13); meta.addView(progress); add(page,meta,-2,16);
        add(page,title("Qual é a palavra?",29),-2,10);
        LinearLayout card=column(); card.setPadding(dp(14),dp(8),dp(14),dp(14)); card.setGravity(Gravity.CENTER); card.setBackground(background(Color.WHITE,24)); add(page,card,-2,12);
        image=new ImageView(this); image.setScaleType(ImageView.ScaleType.FIT_CENTER); image.setAdjustViewBounds(true);
        image.setContentDescription(engine.picture?engine.current.clue:"Imagem disponível como ajuda");
        if(engine.picture) loadPicture(); else image.setImageDrawable(new GardenDrawable());
        add(card,image,150,0);
        if(engine.level==3) {
            TextView clue=label(engine.current.clue,16); clue.setGravity(Gravity.CENTER); add(card,clue,-2,4);
            LinearLayout clueActions=row();
            Button read=button("♫  Ouvir pista",false,() -> speak(engine.current.clue));
            read.setEnabled(audio); if(!audio)read.setText("♫  Som desligado");
            Button show=button("▧  Ver imagem",false,() -> { engine.picture=true; engine.assisted=true; loadPicture(); message="Olhe a imagem. Ela é uma pista!"; updateRound(); }); imageButton=show;
            clueActions.addView(read,new LinearLayout.LayoutParams(0,dp(48),1)); LinearLayout.LayoutParams sp=new LinearLayout.LayoutParams(0,dp(48),1); sp.setMargins(dp(6),0,0,0); clueActions.addView(show,sp); add(card,clueActions,-2,8);
        }
        slots=row(); slots.setGravity(Gravity.CENTER); add(card,slots,60,8);
        feedback=label(message,16); feedback.setGravity(Gravity.CENTER); feedback.setAccessibilityLiveRegion(View.ACCESSIBILITY_LIVE_REGION_POLITE); feedback.setPadding(dp(4),dp(4),dp(4),dp(4)); add(page,feedback,-2,10);
        TextView choose=title("ESCOLHA UMA LETRA",12); choose.setGravity(Gravity.CENTER); add(page,choose,-2,8);
        keyboard=column(); float screenDp=getResources().getDisplayMetrics().widthPixels/getResources().getDisplayMetrics().density; int columns=engine.level==1?4:(screenDp<360?5:screenDp<400?6:7); List<String> keys=engine.keys();
        for(int at=0;at<keys.size();at+=columns) {
            LinearLayout line=row();
            for(int i=0;i<columns;i++) {
                if(at+i>=keys.size()) { line.addView(new View(this),new LinearLayout.LayoutParams(0,dp(50),1)); continue; }
                String letter=keys.get(at+i); Button key=button(letter,false,() -> select(letter)); key.setTextSize(engine.level==1?24:19); key.setMinWidth(0); key.setMinimumWidth(0); key.setPadding(0,0,0,0);
                LinearLayout.LayoutParams kp=new LinearLayout.LayoutParams(0,dp(50),1); kp.setMargins(dp(2),dp(3),dp(2),dp(3)); line.addView(key,kp); keyViews.put(letter,key);
            }
            add(keyboard,line,-2,0);
        }
        add(page,keyboard,-2,4);
        LinearLayout actions=row();
        soundButton=button("♫  Ouvir palavra",false,() -> { if(engine.level==3 && !engine.completed)engine.assisted=true; speak(engine.current.audio); });
        helpButton=button("✦  Uma ajudinha",false,this::giveHelp);
        actions.addView(soundButton,new LinearLayout.LayoutParams(0,dp(54),1)); LinearLayout.LayoutParams hp=new LinearLayout.LayoutParams(0,dp(54),1); hp.setMargins(dp(7),0,0,0); actions.addView(helpButton,hp); add(page,actions,-2,12);
        nextButton=button("Próxima palavra  →",true,this::nextRound); add(page,nextButton,54,10);
        Button instructions=button(audio?"♫  Como brincar":"♫  Som desligado",false,() -> speak("Toque nas letras para descobrir a palavra. Para ouvir, toque em ouvir palavra. Se precisar, peça uma ajudinha. Depois de completar, toque em próxima palavra.")); instructions.setEnabled(audio); add(page,instructions,48,12);
        updateRound();
    }
    private void loadPicture() {
        try(InputStream in=getAssets().open(engine.current.image.replaceFirst("^/",""))) {
            image.setImageDrawable(Drawable.createFromStream(in,null)); image.setContentDescription(engine.current.clue);
        } catch(IOException e) { image.setImageDrawable(new GardenDrawable()); image.setContentDescription("Imagem indisponível. "+engine.current.clue); }
    }
    private void select(String letter) {
        boolean alreadyComplete=engine.completed;
        if(!engine.guess(letter))return;
        if(engine.contains(letter)) message="Isso! Você encontrou a letra "+letter+".";
        else {
            message="Vamos tentar outra letra?";
            if(hints && engine.mistakes%3==0) { engine.picture=true; loadPicture(); engine.highlight(); message="Vamos tentar outra letra? As teclas com estrela podem ajudar!"; }
        }
        updateRound(); if(!alreadyComplete && engine.completed)finishRound();
    }
    private void giveHelp() {
        if(!hints || engine.current==null || engine.completed)return;
        engine.assisted=true;
        engine.picture=true; loadPicture();
        if(engine.helpStage==0) { speak(engine.current.audio); message="Ouça e olhe a imagem. Pode tentar com calma!"; }
        else if(engine.helpStage==1) { engine.highlight(); message="Procure nas teclas com estrela. Uma delas faz parte da palavra!"; }
        else { engine.reveal(); message="Uma letra apareceu para ajudar. Vamos juntos!"; }
        engine.helpStage++; updateRound(); if(engine.completed)finishRound();
    }
    private void updateRound() {
        if(engine.current==null)return;
        slots.removeAllViews();
        int count=engine.current.word.length();
        for(int i=0;i<count;i++) {
            TextView slot=title(engine.visible(i)?engine.current.word.substring(i,i+1):"_",26); slot.setGravity(Gravity.CENTER); slot.setBackground(background(engine.visible(i)?Color.rgb(227,240,217):CREAM,10));
            slot.setContentDescription(engine.visible(i)?"Letra "+engine.current.word.substring(i,i+1):"Letra ainda não descoberta");
            LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(0,dp(51),1); p.setMargins(dp(2),0,dp(2),0); slots.addView(slot,p);
        }
        for(Map.Entry<String,Button> entry:keyViews.entrySet()) {
            String l=entry.getKey(); Button k=entry.getValue(); boolean chosen=engine.chosen.contains(l);
            k.setEnabled(!chosen && !engine.completed);
            k.setAlpha(1f);
            k.setText(chosen?l+(engine.contains(l)?" ✓":" ·"):l+(engine.highlighted.contains(l)?" ★":""));
            k.setTextSize(chosen?16:(engine.level==1?24:19));
            k.setBackground(background(chosen?(engine.contains(l)?Color.rgb(218,236,212):Color.rgb(239,232,221)):(engine.highlighted.contains(l)?GOLD:Color.rgb(236,239,228)),12));
            k.setTextColor(INK); k.setContentDescription("Letra "+l+(chosen?(engine.contains(l)?", encontrada":", já tentada"):engine.highlighted.contains(l)?", opção destacada":""));
        }
        feedback.setText(engine.completed?"✿ Muito bem! Você descobriu "+engine.current.word+"!":message);
        nextButton.setVisibility(engine.completed?View.VISIBLE:View.GONE);
        helpButton.setEnabled(hints && !engine.completed); helpButton.setAlpha(helpButton.isEnabled()?1f:0.5f);
        helpButton.setText(hints?"✦  Uma ajudinha":"✦  Pistas desligadas");
        soundButton.setText(audio?"♫  Ouvir palavra":"♫  Som desligado");
        soundButton.setEnabled(audio); soundButton.setAlpha(audio?1f:0.5f);
        if(imageButton!=null) { imageButton.setEnabled(!engine.picture); imageButton.setText(engine.picture?"▧  Imagem revelada":"▧  Ver imagem"); }
        progress.setText("✿ "+completedCount()+" descobertas");
    }
    private void finishRound() {
        if(celebrationRecorded)return;
        celebrationRecorded=true; engine.picture=true; loadPicture(); record(true); updateRound(); speak("Muito bem! "+engine.current.audio);
        if(!reduced)for(int i=0;i<slots.getChildCount();i++) {
            final View slot=slots.getChildAt(i);
            Runnable task=() -> { slot.animate().translationY(-dp(7)).setDuration(170).withEndAction(() -> slot.animate().translationY(0).setDuration(170).start()).start(); };
            animationTasks.add(task); handler.postDelayed(task,200L*i);
        }
    }
    private void clearAnimations() { for(Runnable task:animationTasks)handler.removeCallbacks(task); animationTasks.clear(); }
    private void record(boolean complete) {
        if(engine.current==null)return;
        try {
            JSONObject item=history.optJSONObject(engine.current.word); if(item==null)item=new JSONObject();
            if(!complete)item.put("practiced",item.optInt("practiced")+1);
            else { item.put("completed",item.optInt("completed")+1); if(engine.assisted)item.put("assisted",item.optInt("assisted")+1); }
            history.put(engine.current.word,item); prefs.edit().putString("history",history.toString()).apply();
        } catch(JSONException ignored) { }
    }
    private int completedCount() { int n=0; Iterator<String> keys=history.keys(); while(keys.hasNext()) { JSONObject i=history.optJSONObject(keys.next()); if(i!=null && i.optInt("completed")>0)n++; } return n; }
    private void speak(String text) {
        if(!audio)return;
        if(!voiceReady || tts==null) { Toast.makeText(this,"Voz pt-BR offline indisponível. O jogo continua com imagens. Veja Responsáveis.",Toast.LENGTH_SHORT).show(); return; }
        tts.stop(); tts.speak(text,TextToSpeech.QUEUE_FLUSH,null,"aventura");
    }
    private void showParents() {
        if(tts!=null)tts.stop();
        ScrollView scroll=new ScrollView(this); LinearLayout body=column(); body.setPadding(dp(20),dp(8),dp(20),dp(16)); scroll.addView(body);
        add(body,label("Tudo fica neste aparelho. Sem cadastro, anúncios, compras ou envio de dados.",15),-2,4);
        add(body,title("Nível de descoberta",18),-2,16); RadioGroup modes=new RadioGroup(this);
        for(int i=0;i<3;i++) { RadioButton b=new RadioButton(this); b.setId(100+i); b.setText(LEVELS[i]+" · "+(i==0?40:i==1?35:25)+" palavras"); b.setTextColor(INK); modes.addView(b); } modes.check(99+engine.level); add(body,modes,-2,6);
        add(body,label("1. Imagem, fala inicial e 8 letras.\n2. Imagem e teclado completo.\n3. Pista inicial; imagem e palavra falada como ajuda.\nA dificuldade só muda por sua escolha.",14),-2,4);
        add(body,title("Categorias",18),-2,16); List<CheckBox> cats=new ArrayList<>();
        for(int i=0;i<CATEGORIES.length;i++) { CheckBox c=new CheckBox(this); c.setText(CAT_NAMES[i]); c.setChecked(engine.categories.contains(CATEGORIES[i])); cats.add(c); add(body,c,-2,0); }
        CheckBox sounds=new CheckBox(this); sounds.setText("Ativar sons e voz"); sounds.setChecked(audio); add(body,sounds,-2,12);
        CheckBox clues=new CheckBox(this); clues.setText("Ativar pistas graduais e ajuda automática"); clues.setChecked(hints); add(body,clues,-2,0);
        CheckBox motion=new CheckBox(this); motion.setText("Reduzir animações"); motion.setChecked(reduced); add(body,motion,-2,0);
        add(body,title("Voz e escrita",18),-2,16);
        add(body,label(voiceReady?"Voz pt-BR local disponível. Uma nova fala interrompe a anterior.":"Voz pt-BR offline indisponível ou ainda inicializando. Instale uma voz de português brasileiro nas configurações de síntese de voz do Android. O apoio visual funciona sem voz.",14),-2,6);
        add(body,label("A tecla A revela Á, Ã e Â com a grafia correta; as demais vogais seguem a mesma regra. Ç tem tecla própria. O nome da letra não é apresentado como seu som. Não usamos divisão silábica automática.",14),-2,8);
        add(body,title("Palavras praticadas",18),-2,18);
        List<String> practiced=new ArrayList<>(); Iterator<String> it=history.keys(); while(it.hasNext())practiced.add(it.next()); Collections.sort(practiced);
        StringBuilder text=new StringBuilder();
        for(String w:practiced) { JSONObject h=history.optJSONObject(w); text.append(w).append(" · ").append(h.optInt("practiced")).append(" prática(s), ").append(h.optInt("completed")).append(" conclusão(ões), ").append(h.optInt("assisted")).append(" com ajuda\n"); }
        add(body,label(text.length()==0?"As primeiras descobertas aparecerão aqui.":text.toString(),14),-2,8);
        AlertDialog dialog=new AlertDialog.Builder(this).setTitle("Área dos responsáveis").setView(scroll).setPositiveButton("Salvar",null).setNegativeButton("Voltar",null).create();
        add(body,button("Apagar progresso…",false,() -> new AlertDialog.Builder(this).setTitle("Apagar todas as descobertas?").setMessage("As palavras praticadas e as conclusões com ajuda serão apagadas apenas neste aparelho. As preferências serão mantidas.").setNegativeButton("Cancelar",null).setPositiveButton("Apagar",(d,w) -> { history=new JSONObject(); prefs.edit().remove("history").apply(); engine.seen.clear(); dialog.dismiss(); if(started)nextRound(); else showWelcome(); }).show()),52,14);
        dialog.setOnShowListener(d -> dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v -> {
            Set<String> selected=new HashSet<>(); for(int i=0;i<cats.size();i++)if(cats.get(i).isChecked())selected.add(CATEGORIES[i]);
            if(selected.isEmpty()) { Toast.makeText(this,"Escolha pelo menos uma categoria.",Toast.LENGTH_SHORT).show(); return; }
            int level=modes.getCheckedRadioButtonId()-99;
            boolean changed=level!=engine.level || !selected.equals(engine.categories);
            audio=sounds.isChecked(); hints=clues.isChecked(); reduced=motion.isChecked(); engine.level=level; engine.categories=selected;
            if(!hints)engine.highlighted.clear();
            prefs.edit().putBoolean("audio",audio).putBoolean("hints",hints).putBoolean("reduced",reduced).putInt("level",level).putStringSet("categories",selected).apply();
            if(!audio && tts!=null)tts.stop(); dialog.dismiss();
            if(started) { if(changed)nextRound(); else if(engine.current==null)showSequenceEnd(); else showGame(); } else showWelcome();
        })); dialog.show();
    }
    @Override public boolean onKeyDown(int keyCode, KeyEvent event) {
        int unicode=event.getUnicodeChar();
        if(started && engine.current!=null && unicode!=0) {
            String key=GameEngine.base(String.valueOf((char)unicode));
            if(key.length()==1 && engine.keys().contains(key)) { select(key); return true; }
        }
        return super.onKeyDown(keyCode,event);
    }
    @Override protected void onStop() { super.onStop(); if(tts!=null)tts.stop(); clearAnimations(); }
    @Override protected void onDestroy() { if(tts!=null)tts.shutdown(); clearAnimations(); super.onDestroy(); }

    /** A quiet garden mascot; content illustrations are separate local PNGs. */
    private final class GardenView extends View {
        private final Paint paint=new Paint(Paint.ANTI_ALIAS_FLAG);
        GardenView(Context c) { super(c); setContentDescription("Lili, uma flor sorridente, no jardim"); }
        @Override protected void onDraw(Canvas c) { super.onDraw(c); drawGarden(c,getWidth(),getHeight(),paint); }
    }
    private final class GardenDrawable extends Drawable {
        private final Paint paint=new Paint(Paint.ANTI_ALIAS_FLAG);
        public void draw(Canvas c) { drawGarden(c,getBounds().width(),getBounds().height(),paint); }
        public void setAlpha(int a){} public void setColorFilter(ColorFilter f){} public int getOpacity(){return android.graphics.PixelFormat.TRANSLUCENT;}
    }
    private void drawGarden(Canvas c,float w,float h,Paint p) {
        c.save(); c.scale(w/360f,h/200f);
        p.setColor(Color.rgb(226,236,208)); c.drawOval(-30,147,390,280,p);
        p.setColor(GREEN); p.setStrokeWidth(8); c.drawLine(180,94,180,182,p); c.drawOval(132,129,181,153,p); c.drawOval(180,142,225,166,p);
        p.setColor(Color.rgb(240,180,154));
        for(int i=0;i<7;i++) { double a=i*Math.PI*2/7; c.drawCircle(180+(float)Math.cos(a)*34,79+(float)Math.sin(a)*34,25,p); }
        p.setColor(GOLD); c.drawCircle(180,79,31,p);
        p.setColor(INK); c.drawCircle(170,76,3,p); c.drawCircle(190,76,3,p); p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(2.5f); c.drawArc(170,77,190,92,0,180,false,p); p.setStyle(Paint.Style.FILL);
        p.setColor(Color.rgb(250,216,125)); c.drawCircle(300,30,17,p);
        p.setColor(Color.WHITE); c.drawOval(45,29,105,48,p); c.drawOval(66,18,99,49,p);
        c.restore();
    }
}
