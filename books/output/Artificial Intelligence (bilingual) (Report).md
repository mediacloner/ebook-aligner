# Bilingual Alignment Verification Report

**Generated:** 2026-01-12 01:20:01
**Output File:** `bilingual_aligned.epub`
**Alignment Mode:** 📝 Preserve Paragraphs

## Summary

- **Total pairs analyzed:** 1856
- **Flagged as suspicious:** 614
- **Automatically Fixed:** 614
  - 🔍 Vector Search: 5
  - ✨ LLM Repair: 94
- **Pass rate:** 66.9%
- **Avg Chunk Length:** EN: 318.4 chars | ES: 387.2 chars (Ratio: 1.22)
- **Pass rate with Vector Search:** 67.2%

## Flagged & Fixed Pairs

The following translation pairs were identified as misaligned:

### Issue 1 📏 OVER-LONG (FIXED)

**English:** FIGURE 3: An illustration of a perceptron that recognizes handwritten 8s. Each pixel in the 18 × 18–pixel image corresponds to an input for the perceptron, yielding 324 (= 18 × 18) inputs.

**Original Spanish:** La figura 3A muestra un ocho manuscrito ampliado. Cada elemento de la cuadrícula es un píxel con un ...

**📏 LLM Resized:** FIGURA 3: Una ilustración de un perceptrón que reconoce ochos escritos a mano. Cada pixel en la imagen de 18 × 18 pixels corresponde a una entrada para el perceptrón, lo que resulta en 324 (= 18 × 18)...

**Confidence:** 0.15

---

### Issue 2 ✅ FIXED

**English:** An 8 detector is useful if you care only about 8s. But what about recognizing other digits? It’s fairly straightforward to extend our perceptron to have ten outputs, one for each digit. Given an examp...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Un detector de 8 es útil si solo te preocupas por los 8s. Pero ¿qué pasa con reconocer otros dígitos? Es relativamente fácil ampliar nuestro perceptrón para que tenga diez salidas, una para cada dígit...

**Confidence:** 0.05

---

### Issue 3 ✅ FIXED

**English:** Think of the structure of your brain, in which some neurons directly control “outputs” such as your muscle movements but most neurons simply communicate with other neurons. These could be called the b...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Piense en la estructura de su cerebro, donde algunos neuronas controlan directamente "salidas" como sus movimientos musculares pero la mayoría simplemente se comunican con otras neuronas. Estas podría...

**Confidence:** 0.05

---

### Issue 4 ✅ FIXED

**English:** The network shown in figure 4 is referred to as “multilayered” because it has two layers of units (hidden and output) instead of just an output layer. In principle, a multilayer network can have multi...

**Original Spanish:** (empty)

**🆕 LLM Generated:** La red representada en la figura 4 se conoce como "multicapa" debido a que tiene dos capas de unidades (oculta y de salida) en lugar de simplemente una capa de salida. En principio, una red multicapa ...

**Confidence:** 0.05

---

### Issue 5 ✅ FIXED

**English:** Similar to perceptrons, each unit here multiplies each of its inputs by the weight on that input’s connection and then sums the results. However, unlike in a perceptron, a unit here doesn’t simply “fi...

**Original Spanish:** (empty)

**🆕 LLM Generated:** De manera similar a los perceptrones, cada unidad aquí multiplica cada una de sus entradas por el peso en la conexión de esa entrada y luego suma los resultados. Sin embargo, a diferencia de un percep...

**Confidence:** 0.05

---

### Issue 6 ✅ FIXED

**English:** To process an image such as the handwritten 8 in figure 4, the network performs its computations layer by layer, from left to right. Each hidden unit computes its activation value; these activation va...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Para procesar una imagen como el número 8 manuscrito en la figura 4, la red realiza sus cálculos capa por capa, de izquierda a derecha. Cada unidad oculta calcula su valor de activación; estos valores...

**Confidence:** 0.05

---

### Issue 7 ✅ FIXED

**English:** In principle, a multilayer neural network can learn to use its hidden units to recognize more abstract features (for example, visual shapes, such as the top and bottom “circles” on a handwritten 8) th...

**Original Spanish:** (empty)

**🆕 LLM Generated:** En principio, una red neuronal de capas múltiples puede aprender a usar sus unidades ocultas para reconocer características más abstractas (por ejemplo, formas visuales como las "cimas" y "bases" de u...

**Confidence:** 0.05

---

### Issue 8 ✅ FIXED

**English:** Learning via Back-Propagation

**Original Spanish:** (empty)

**🆕 LLM Generated:** Aprendizaje mediante Retropropagación ±

**Confidence:** 0.05

---

### Issue 9 ✅ FIXED

**English:** In their book Perceptrons, Minsky and Papert were skeptical that a successful algorithm could be designed for learning the weights in a multilayer neural network. Their skepticism (along with doubts f...

**Original Spanish:** (empty)

**🆕 LLM Generated:** En su libro "Perceptrones", Minsky y Papert eran escépticos de que se pudiera diseñar un algoritmo exitoso para aprender los pesos en una red neuronal multilayer. Su escepticismo (junto con las dudas ...

**Confidence:** 0.05

---

### Issue 10 ✅ FIXED

**English:** As its name implies, back-propagation is a way to take an error observed at the output units (for example, a high confidence for the wrong digit in the example of figure 4) and to “propagate” the blam...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Como su nombre sugiere, la retropropagación es una forma de tomar un error observado en las unidades de salida (por ejemplo, una alta confianza en el dígito incorrecto en el ejemplo de la figura 4) y ...

**Confidence:** 0.05

---

### Issue 11 ✅ FIXED

**English:** Back-propagation will work (in principle at least) no matter how many inputs, hidden units, or output units your neural network has. While there is no mathematical guarantee that back-propagation will...

**Original Spanish:** (empty)

**🆕 LLM Generated:** La retropropagación funcionará (en principio al menos) sin importar cuántas entradas, unidades ocultas o unidades de salida tenga tu red neuronal. Aunque no hay garantía matemática de que la retroprop...

**Confidence:** 0.05

---

### Issue 12 ✅ FIXED

**English:** It’s important to note that while I’ve used the example of handwritten digits, neural networks can be applied not just to images but to any kind of data. Neural networks have been applied in areas as ...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Es importante tener en cuenta que aunque he utilizado el ejemplo de dígitos escritos a mano, las redes neuronales se pueden aplicar no solo a imágenes sino a cualquier tipo de datos. Las redes neurona...

**Confidence:** 0.05

---

### Issue 13 ✅ FIXED

**English:** In the 1980s, the most visible group working on neural networks was a team at the University of California at San Diego headed by two psychologists, David Rumelhart and James McClelland. What we now c...

**Original Spanish:** (empty)

**🆕 LLM Generated:** En la década de 1980, el grupo más visible que trabajaba en redes neuronales era un equipo de la Universidad de California en San Diego encabezado por dos psicólogos, David Rumelhart y James McClellan...

**Confidence:** 0.05

---

### Issue 14 ✅ FIXED

**English:** Indeed, by the mid-1980s, expert systems—symbolic AI approaches that rely on humans to create rules that reflect expert knowledge of a particular domain—were increasingly revealing themselves to be br...

**Original Spanish:** (empty)

**🆕 LLM Generated:** En efecto, hacia la década del ochenta, los sistemas experto -enfoques de IA simbólica que dependen de los humanos para crear reglas que reflejen el conocimiento experto en un dominio particular- se e...

**Confidence:** 0.05

---

### Issue 15 ✅ FIXED

**English:** According to the proponents of connectionism, the key to intelligence was an appropriate computational architecture—inspired by the brain—and the ability of the system to learn on its own from data or...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Según los defensores del connectionismo, la clave de la inteligencia era una arquitectura computacional adecuada —inspirada en el cerebro— y la capacidad del sistema para aprender por sí mismo a parti...

**Confidence:** 0.05

---

### Issue 16 ✅ FIXED

**English:** Bad at Logic, Good at Frisbee

**Original Spanish:** (empty)

**🆕 LLM Generated:** Pésimo en Lógica, Excelente en Frisbee ±

**Confidence:** 0.05

---

### Issue 17 ✅ FIXED

**English:** Over the last six decades of AI research, people have repeatedly debated the relative advantages and disadvantages of symbolic and subsymbolic approaches. Symbolic systems can be engineered by humans,...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Durante las últimas seis décadas de investigación en IA, se ha discutido reiteradamente sobre las ventajas y desventajas relativas de los enfoques simbólicos y subsimbólicos. Los sistemas simbólicos p...

**Confidence:** 0.05

---

### Issue 18 ✅ FIXED

**English:** In contrast, as we’ve seen, subsymbolic systems tend to be hard to interpret, and no one knows how to directly program complex human knowledge or logic into these systems. Subsymbolic systems seem muc...

**Original Spanish:** (empty)

**🆕 LLM Generated:** En cambio, como hemos visto, los sistemas subsimbólicos suelen ser difíciles de interpretar y nadie sabe cómo programar directamente el conocimiento o la lógica humana compleja en estos sistemas. Los ...

**Confidence:** 0.05

---

### Issue 19 ✅ FIXED

**English:** So, why not just use symbolic systems for tasks that require high-level language-like descriptions and logical reasoning, and use subsymbolic systems for the low-level perceptual tasks such as recogni...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Entonces, ¿por qué no usar sistemas simbólicos para tareas que requieren descripciones de alto nivel y razonamiento lógico, y utilizar sistemas subsimbólicos para las tareas perceptuales de bajo nivel...

**Confidence:** 0.05

---

### Issue 20 ✅ FIXED

**English:** Inspired by statistics and probability theory, AI researchers developed numerous algorithms that enable computers to learn from data, and the field of machine learning became its own independent subdi...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Impulsados por la estadística y la teoría de la probabilidad, los investigadores de IA desarrollaron numerosos algoritmos que permiten a los ordenadores aprender de los datos, y el campo del aprendiza...

**Confidence:** 0.05

---

### Issue 21 ✅ FIXED

**English:** Over the next two decades, machine learning had its own cycles of optimism, government funding, start-ups, and overpromising, followed by the inevitable winters. Training neural networks and similar m...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Durante las dos décadas siguientes, el aprendizaje automático tuvo sus propios ciclos de optimismo, financiamiento gubernamental, empresas emergentes y promesas excessivas, seguidos inevitablemente po...

**Confidence:** 0.05

---

### Issue 22 ✅ FIXED

**English:** Note that this argument is saying the following: (1) Only when a machine feels things and is aware of its own actions and feelings—in short, is conscious—could we consider it actually thinking, and (2...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Ten en cuenta que este argumento sostiene lo siguiente: (1) Solo cuando una máquina siente cosas y es consciente de sus propios actos y sentimientos —en resumen, es consciente—, podríamos considerar q...

**Confidence:** 0.05

---

### Issue 23 ✅ FIXED

**English:** JUDGE: how old are you

**Original Spanish:** (empty)

**🆕 LLM Generated:** Juez: ¿Cuántos años tienes? ±

**Confidence:** 0.05

---

### Issue 24 ✅ FIXED

**English:** Kurzweil was also influenced by the mathematician and science fiction writer Vernor Vinge, who believed this event was close at hand: “The evolution of human intelligence took millions of years. We wi...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Kurzweil también se vio influenciado por el matemático y escritor de ciencia ficción Vernor Vinge, quien creía que este evento estaba cerca: "La evolución de la inteligencia humana llevó millones de a...

**Confidence:** 0.05

---

### Issue 25 ✅ FIXED

**English:** Douglas Hofstadter is one thinker who—again surprising me—straddles the fence between Singularity skepticism and worry. He was disturbed, he told me, that Kurzweil’s books “mixed in the zaniest scienc...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Douglas Hofstadter es uno de los pensadores que—a mi sorpresa—oscila entre el escepticismo y la preocupación acerca del llamado "canto del cisne". Se mostró preocupado, como me contó, por cómo Kurzwei...

**Confidence:** 0.05

---

### Issue 26 ✅ FIXED

**English:** AI researchers are a competitive bunch, so it’s no surprise that they like to organize competitions to drive the field forward. In the field of visual object recognition, researchers have long held an...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Investigadores de IA son un grupo competitivo, así que no es sorpresa que les guste organizar competencias para impulsar el campo hacia adelante. En el campo del reconocimiento de objetos visuales, lo...

**Confidence:** 0.05

---

### Issue 27 ✅ FIXED

**English:** The term long tail comes from statistics, in which certain probability distributions are shaped like the one in figure 13: the long list of very unlikely (but possible) situations is called the “tail”...

**Original Spanish:** (empty)

**🆕 LLM Generated:** El término "cola larga" proviene de las estadísticas, donde ciertas distribuciones de probabilidad tienen la forma de la figura 13: la larga lista de situaciones muy improbables (pero posibles) se lla...

**Confidence:** 0.05

---

### Issue 28 ✅ FIXED

**English:** Here are two real-world examples. In March 2016, there was a massive snowstorm forecast in the Northeast of the United States, and reports appeared on Twitter that Tesla vehicles’ Autopilot mode, whic...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Aquí hay dos ejemplos del mundo real. En marzo de 2016, se anunció una gran nevada en el Noreste de los Estados Unidos, y aparecieron informes en Twitter que los vehículos Tesla en modo Autopilot, que...

**Confidence:** 0.05

---

### Issue 29 ✅ FIXED

**English:** Companies working on autonomous-vehicle technology are acutely aware of the long-tail problem: their teams brainstorm possible long-tail scenarios and actively create extra training examples as well a...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Empresas que trabajan en tecnología de vehículos autónomos son muy conscientes del problema de la cola larga: sus equipos brainstormen posibles escenarios de cola larga y crean activamente ejemplos ad...

**Confidence:** 0.05

---

### Issue 30 ✅ FIXED

**English:** FIGURE 14: Salt lines on a highway, in advance of a forecasted snowstorm, were reported to be confusing Tesla’s Autopilot feature.

**Original Spanish:** (empty)

**🆕 LLM Generated:** FIGURA 14: Se informaron líneas de sal en una autopista, antes de una tormenta de nieve prevista, que confundían la función Autopilot de un Tesla. ±

**Confidence:** 0.05

---

### Issue 31 ✅ FIXED

**English:** A commonly proposed solution is for AI systems to use supervised learning on small amounts of labeled data and learn everything else via unsupervised learning. The term unsupervised learning refers to...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Una solución comúnmente propuesta es que los sistemas de IA utilicen aprendizaje supervisado en pequeñas cantidades de datos etiquetados y aprendan todo lo demás mediante aprendizaje no supervisado. E...

**Confidence:** 0.05

---

### Issue 32 ✅ FIXED

**English:** Humans make mistakes all the time, even (or especially) in driving; any one of us might have hit that public bus, had we been the one veering around sandbags. But humans also have a fundamental compet...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Los humanos cometemos errores todo el tiempo, incluso (o especialmente) al conducir; cualquiera de nosotros podría haber golpeado ese autobús público si hubiéramos sido los que doblábamos alrededor de...

**Confidence:** 0.05

---

### Issue 33 ✅ FIXED

**English:** A few years ago, Will Landecker, then a graduate student in my research group, trained a deep neural network to classify photographs into one of two categories: “contains an animal” and “does not cont...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Hace unos años, Will Landecker, en ese momento un estudiante de posgrado en mi grupo de investigación, entrenó una red neuronal profunda para clasificar fotografías en una de dos categorías: "contiene...

**Confidence:** 0.05

---

### Issue 34 ✅ FIXED

**English:** FIGURE 15: Illustration of “animal” versus “no animal” classification task. Note the blurry background in the image on the left.

**Original Spanish:** (empty)

**🆕 LLM Generated:** FIGURA 15: Ilustración de la tarea de clasificación "animal" frente a "sin animal". Observe el fondo borroso en la imagen de la izquierda. ±

**Confidence:** 0.05

---

### Issue 35 ✅ FIXED

**English:** This is an example of a common phenomenon seen in machine learning. The machine learns what it observes in the data rather than what you (the human) might observe. If there are statistical association...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Este es un ejemplo de un fenómeno común visto en aprendizaje automático. La máquina aprende lo que observa en los datos en lugar de lo que tú (el ser humano) podría observar. Si hay asociaciones estad...

**Confidence:** 0.05

---

### Issue 36 ✅ FIXED

**English:** In recent years, several research teams have investigated whether ConvNets trained on ImageNet and other large data sets have likewise overfitted to their training data. One group showed that if ConvN...

**Original Spanish:** (empty)

**🆕 LLM Generated:** En años recientes, varios equipos de investigación han explorado si las ConvNets entrenadas en ImageNet y otros conjuntos de datos grandes han sobreajustado a sus datos de entrenamiento. Un grupo demo...

**Confidence:** 0.05

---

### Issue 37 ✅ FIXED

**English:** FIGURE 16: Labels assigned to photos by Google’s automated photo tagger, including the infamous “Gorillas” tag

**Original Spanish:** (empty)

**🆕 LLM Generated:** FIGURA 16: Etiquetas asignadas a fotos por el etiquetador automático de fotos de Google, incluyendo la famosa etiqueta "Gorilas" ±

**Confidence:** 0.05

---

### Issue 38 ✅ FIXED

**English:** The unreliability of ConvNets can result in embarrassing—and potentially damaging—errors. Google suffered a public relations nightmare in 2015 after it rolled out an automated photo-tagging feature (u...

**Original Spanish:** (empty)

**🆕 LLM Generated:** La falta de fiabilidad de los ConvNets puede dar lugar a errores bochornosos e incluso perjudiciales. Google sufrió una pesadilla de relaciones públicas en 2015 después de lanzar una función de etique...

**Confidence:** 0.05

---

### Issue 39 ✅ FIXED

**English:** FIGURE 17: Example of a camera face-detection program identifying an Asian face as “blinking”

**Original Spanish:** (empty)

**🆕 LLM Generated:** FIGURA 17: Ejemplo de un programa de detección facial de cámara que identifica un rostro asiático como "parpadeando" ±

**Confidence:** 0.05

---

### Issue 40 ✅ FIXED

**English:** Such repellent and widely mocked misclassifications are embarrassing for the companies involved, but more subtle errors due to racial or gender biases have been noted frequently in vision systems powe...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Tales errores repelentes y ampliamente ridiculizados son embarazosos para las empresas involucradas, pero se han observado con frecuencia errores más sutiles debido a sesgos raciales o de género en si...

**Confidence:** 0.05

---

### Issue 41 ✅ FIXED

**English:** Kate Crawford, a researcher at Microsoft and an activist for fairness and transparency in AI, pointed out that one widely used data set for training face-recognition systems contains faces that are 77...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Kate Crawford, investigadora de Microsoft y activista por la equidad y transparencia en el aprendizaje automático, observó que un conjunto de datos ampliamente utilizado para entrenar sistemas de reco...

**Confidence:** 0.05

---

### Issue 42 ✅ FIXED

**English:** Of course, these biases in AI training data reflect biases in our society, but the spread of real-world AI systems trained on biased data can magnify these biases and do real damage. Face-recognition ...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Por supuesto, estas sesgos en los datos de entrenamiento de IA reflejan sesgos en nuestra sociedad, pero la propagación de sistemas de IA reales entrenados con datos sesgados puede magnificar estos se...

**Confidence:** 0.05

---

### Issue 43 ✅ FIXED

**English:** Such biases can be mitigated in individual data sets by having humans make sure that the photos (or other kinds of data) are balanced in their representation of, say, racial or gender groups. But this...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Estos sesgos pueden mitigarse en conjuntos de datos individuales si los humanos se aseguran de que las fotos (o otros tipos de datos) estén equilibradas en su representación, por ejemplo, de grupos ra...

**Confidence:** 0.05

---

### Issue 44 ✅ FIXED

**English:** The problem of bias in applications of AI has been getting a lot of attention recently, with many articles, workshops, and even academic research institutes devoted to this topic. Should the data sets...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Recientemente, se ha prestado una gran atención al problema del sesgo en las aplicaciones de la IA, con numerosos artículos, talleres e incluso instituciones de investigación académica dedicados a est...

**Confidence:** 0.05

---

### Issue 45 ✅ FIXED

**English:** Remember back in school when your teacher would write “show your work” in red on your math homework? For me, showing my work was the least fun part of learning math but probably the most important, be...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Recuerdas aquellos tiempos en la escuela cuando tu profesor escribía "muestra tu trabajo" en rojo en tus tareas de matemáticas? Para mí, mostrar mi trabajo era la parte menos divertida de aprender mat...

**Confidence:** 0.05

---

### Issue 46 ✅ FIXED

**English:** More generally, you can often trust that people know what they are doing if they can explain to you how they arrived at an answer or a decision. However, “showing their work” is something that deep ne...

**Original Spanish:** (empty)

**🆕 LLM Generated:** De manera más general, con frecuencia se puede confiar en que las personas saben lo que están haciendo si pueden explicar cómo llegaron a una respuesta o decisión. Sin embargo, «demostrar su trabajo» ...

**Confidence:** 0.05

---

### Issue 47 ✅ FIXED

**English:** Humans can’t always explain their thought processes either, and you generally can’t look “under the hood” into other people’s brains (or into their “gut feelings”) to figure out how they came to any p...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Los seres humanos no siempre pueden explicar sus procesos de pensamiento, y generalmente no se puede "mirar debajo del capó" en el cerebro de otras personas (o en sus "sentimientos instintivos") para ...

**Confidence:** 0.05

---

### Issue 48 ✅ FIXED

**English:** It shouldn’t come as a surprise then that one of the hottest new areas of AI is variously called “explainable AI,” “transparent AI,” or “interpretable machine learning.” These terms refer to research ...

**Original Spanish:** (empty)

**🆕 LLM Generated:** No debería sorprender que una de las áreas más recientes y calientes de la IA se llame Variousmente "IA explicable", "IA transparente" o "aprendizaje automático interpretable". Estos términos hacen re...

**Confidence:** 0.05

---

### Issue 49 ✅ FIXED

**English:** Fooling Deep Neural Networks

**Original Spanish:** (empty)

**🆕 LLM Generated:** Engañando Redes Neuronales Profundas ±

**Confidence:** 0.05

---

### Issue 50 ✅ FIXED

**English:** There is yet another dimension to the AI trustworthiness question: Researchers have discovered that it is surprisingly easy for humans to surreptitiously trick deep neural networks into making errors....

**Original Spanish:** (empty)

**🆕 LLM Generated:** Existe otra dimensión en la pregunta sobre la confiabilidad de la IA: los investigadores han descubierto que resulta sorprendentemente fácil para los humanos engañar subrepticiamente a las redes neuro...

**Confidence:** 0.05

---

### Issue 51 ✅ FIXED

**English:** Fooling AI systems is not new. Email spammers, for example, have been in an arms race with spam-detection programs for decades. But the kinds of attacks to which deep-learning systems seem to be vulne...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Engañar sistemas de IA no es algo nuevo. Los spammers de correos electrónicos, por ejemplo, han estado en una carrera armamentista con los programas de detección de spam durante décadas. Pero los tipo...

**Confidence:** 0.05

---

### Issue 52 ✅ FIXED

**English:** Remember AlexNet, which I discussed in chapter 5? It was the convolutional neural network that won the 2012 ImageNet challenge and that set in motion the dominance of ConvNets in much of today’s AI wo...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Recuerda AlexNet, que mencioné en el capítulo 5? Fue la red neuronal convolucional que ganó el desafío ImageNet de 2012 y que inició la dominancia de los ConvNets en gran parte del mundo actual de la ...

**Confidence:** 0.05

---

### Issue 53 ✅ FIXED

**English:** In particular, the paper’s authors had discovered that they could take an ImageNet photo that AlexNet classified correctly with high confidence (for example, “School Bus”) and distort it by making ver...

**Original Spanish:** (empty)

**🆕 LLM Generated:** En particular, los autores del papel habían descubierto que podían tomar una fotografía de ImageNet que AlexNet clasificaba correctamente con alta confianza (por ejemplo, "Autobús Escolar") y distorsi...

**Confidence:** 0.05

---

### Issue 54 ✅ FIXED

**English:** Szegedy and his collaborators created a computer program that could, given any photo from ImageNet that was correctly classified by AlexNet, find specific changes to the photo to create a new adversar...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Szegedy y sus colaboradores crearon un programa de ordenador que podía, dada cualquier foto de ImageNet que hubiera sido clasificada correctamente por AlexNet, encontrar cambios específicos en la foto...

**Confidence:** 0.05

---

### Issue 55 ✅ FIXED

**English:** FIGURE 18: Original and “adversarial” examples for AlexNet. The left image in each pair shows the original image, which was correctly classified by AlexNet. The right image in each pair shows the adve...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Figura 18: Imágenes originales y "adversariales" para AlexNet. La imagen de la izquierda en cada pareja muestra la imagen original, que fue clasificada correctamente por AlexNet. La imagen de la derec...

**Confidence:** 0.05

---

### Issue 56 ✅ FIXED

**English:** Importantly, Szegedy and his collaborators found that this susceptibility to adversarial examples wasn’t special to AlexNet; they showed that several other convolutional neural networks—with different...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Resulta importante que Szegedy y sus colaboradores descubrieron que esta susceptibilidad a los ejemplos adversariales no era exclusiva de AlexNet; demostraron que varias otras redes neuronales convolu...

**Confidence:** 0.05

---

### Issue 57 ✅ FIXED

**English:** Not long after the paper by Szegedy and his colleagues appeared, a group from the University of Wyoming published an article with a more direct title: “Deep Neural Networks Are Easily Fooled.”21 By us...

**Original Spanish:** (empty)

**🆕 LLM Generated:** No mucho después de que apareciera el artículo de Szegedy y sus colegas, un grupo de la Universidad de Wyoming publicó un estudio con un título más directo: “Las redes neuronales profundas son fácilme...

**Confidence:** 0.05

---

### Issue 58 ✅ FIXED

**English:** FIGURE 19: Examples of images created by a genetic algorithm specifically to fool a convolutional neural network. In each case, AlexNet (trained on the ImageNet training set) assigned a confidence gre...

**Original Spanish:** (empty)

**🆕 LLM Generated:** FIGURA 19: Ejemplos de imágenes creadas por un algoritmo genético específicamente para engañar a una red neuronal convolucional. En cada caso, AlexNet (entrenado en el conjunto de entrenamiento ImageN...

**Confidence:** 0.05

---

### Issue 59 ✅ FIXED

**English:** Indeed, these two papers and subsequent related discoveries raised not only questions but also genuine alarm in the deep-learning community. If deep-learning systems, so successful at computer vision ...

**Original Spanish:** (empty)

**🆕 LLM Generated:** En efecto, estos dos documentos y los hallazgos posteriores relacionados han generado no solo preguntas sino también una alarma genuina en la comunidad de aprendizaje profundo. Si los sistemas de apre...

**Confidence:** 0.05

---

### Issue 60 ✅ FIXED

**English:** All this has reenergized the small research community focusing on “adversarial learning”—that is, developing strategies that defend against potential (human) adversaries who could attack machine-learn...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Todo esto ha revitalizado a la pequeña comunidad de investigación centrada en "el aprendizaje adversarial" -es decir, desarrollar estrategias que se defiendan contra posibles adversarios humanos que p...

**Confidence:** 0.05

---

### Issue 61 ✅ FIXED

**English:** FIGURE 20: An AI researcher (left) wearing eyeglass frames with a pattern specially designed to cause a deep neural network face recognizer, trained on celebrity faces, to confidently classify the lef...

**Original Spanish:** (empty)

**🆕 LLM Generated:** FIGURA 20: Un investigador de IA (izquierda) usando gafas con un patrón especialmente diseñado para hacer que un sistema de reconocimiento facial basado en redes neuronales profundas, entrenado con ca...

**Confidence:** 0.05

---

### Issue 62 ✅ FIXED

**English:** These are just a few examples of possible attacks that have been concocted by various research groups. Many of the possible attacks have been shown to be surprisingly robust: they work on several diff...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Estos son solo unos pocos ejemplos de posibles ataques que han sido ideados por diferentes grupos de investigación. Muchos de los posibles ataques se han demostrado ser sorprendentemente robustos: fun...

**Confidence:** 0.05

---

### Issue 63 ✅ FIXED

**English:** Understanding and defending against such potential attacks are a major area of research right now, but while researchers have found solutions for specific kinds of attacks, there is still no general d...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Entender y defenderse contra tales posibles ataques es un área principal de investigación en la actualidad, aunque los investigadores han encontrado soluciones para tipos específicos de ataques, aún n...

**Confidence:** 0.05

---

### Issue 64 ✅ FIXED

**English:** Beyond the immediate issue of how to defend against attacks, the existence of adversarial examples amplifies the question I asked earlier: What, precisely, are these networks learning? In particular, ...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Más allá del problema inmediato de cómo defenderse contra los ataques, la existencia de ejemplos adversariales amplifica la pregunta que planteé antes: ¿Qué, exactamente, están aprendiendo estas redes...

**Confidence:** 0.05

---

### Issue 65 ✅ FIXED

**English:** To my mind, the ultimate problem is one of understanding. Consider figure 18, where AlexNet mistakes a school bus for an ostrich. Why would this be very unlikely to happen to a human? Even though Alex...

**Original Spanish:** (empty)

**🆕 LLM Generated:** A mi entender, el problema fundamental es uno de comprensión. Consideren la figura 18, donde AlexNet confunde un autobús escolar con un avestruz. ¿Por qué sería muy poco probable que esto ocurriera a ...

**Confidence:** 0.05

---

### Issue 66 ✅ FIXED

**English:** FIGURE 21: A visual illusion for humans: the horizontal line segments in A and B are the same length, but most people perceive the segment in A to be longer than the one in B.

**Original Spanish:** (empty)

**🆕 LLM Generated:** Figure 21: Una ilusión visual para los humanos: los segmentos de línea horizontal en A y B tienen la misma longitud, pero la mayoría de las personas perciben que el segmento en A es más largo que el d...

**Confidence:** 0.05

---

### Issue 67 ✅ FIXED

**English:** I’ve heard some AI researchers argue that humans are also susceptible to our own types of “adversarial examples”: visual illusions. Like AlexNet classifying a school bus as an ostrich, humans are susc...

**Original Spanish:** (empty)

**🆕 LLM Generated:** He oído a algunos investigadores de IA argumentar que los humanos también somos susceptibles a nuestros propios tipos de "ejemplos adversarios": ilusiones visuales. Como AlexNet clasificando un autobú...

**Confidence:** 0.05

---

### Issue 68 ✅ FIXED

**English:** Jeff Clune, an AI researcher at the University of Wyoming, made a very provocative analogy when he noted that there is “a lot of interest in whether Deep Learning is ‘real intelligence’ or a ‘Clever H...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Jeff Clune, investigador de IA en la Universidad de Wyoming, realizó una analogía muy provocativa al observar que hay "mucho interés en saber si el aprendizaje profundo es 'inteligencia real' o un 'Cl...

**Confidence:** 0.05

---

### Issue 69 ✅ FIXED

**English:** On the one hand, deep neural networks, trained via supervised learning, perform remarkably well (though still far from perfectly) on many problems in computer vision, as well as in other domains such ...

**Original Spanish:** (empty)

**🆕 LLM Generated:** De un lado, las redes neuronales profundas, entrenadas mediante aprendizaje supervisado, presentan un desempeño notable (aunque aún lejos de la perfección) en muchos problemas de visión por computador...

**Confidence:** 0.05

---

### Issue 70 ✅ FIXED

**English:** In a blog post on his company’s website, Microsoft’s president and chief legal officer, Brad Smith, called for Congress to regulate face recognition:

**Original Spanish:** (empty)

**🆕 LLM Generated:** En una entrada en su blog en el sitio web de la empresa, el presidente y jefe de abogados de Microsoft, Brad Smith, pidió a los miembros del Congreso que regulen la reconocimiento facial. ±

**Confidence:** 0.05

---

### Issue 71 ✅ FIXED

**English:** Facial recognition technology raises issues that go to the heart of fundamental human rights protections like privacy and freedom of expression. These issues heighten responsibility for tech companies...

**Original Spanish:** (empty)

**🆕 LLM Generated:** La tecnología de reconocimiento facial plantea cuestiones que afectan derechos fundamentales como la privacidad y la libertad de expresión. Estos problemas agudizan la responsabilidad de las empresas ...

**Confidence:** 0.05

---

### Issue 72 ✅ FIXED

**English:** Google followed suit, announcing that it would not offer general-purpose face-recognition services via its cloud AI platform until the company can “ensure its use is aligned with our principles and va...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Google siguió el ejemplo de sus competidores, anunciando que no ofrecería servicios generales de reconocimiento facial a través de su plataforma de inteligencia artificial en la nube hasta que la empr...

**Confidence:** 0.05

---

### Issue 73 ✅ FIXED

**English:** The response of these companies is encouraging, but it brings to the forefront another vexing issue: To what extent should AI research and development be regulated, and who should do the regulating?

**Original Spanish:** (empty)

**🆕 LLM Generated:** La respuesta de estas empresas es alentadora, pero plantea otro problema preocupante: ¿En qué medida debería regularse la investigación y desarrollo de IA, y quién debería hacerlo? ±

**Confidence:** 0.05

---

### Issue 74 ✅ FIXED

**English:** Given the risks of AI technologies, many practitioners of AI, myself included, are in favor of some kind of regulation. But the regulation shouldn’t be left solely in the hands of AI researchers and c...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Dadas las implicaciones de los avances tecnológicos en Inteligencia Artificial, muchos profesionales de este campo, yo entre ellos, somos partidarios de alguna clase de regulación. Sin embargo, esta r...

**Confidence:** 0.05

---

### Issue 75 ✅ FIXED

**English:** In one example of the complexity of crafting such regulations, in 2018 the European Parliament enacted a regulation on AI that some have called the “right to explanation.”11 This regulation requires, ...

**Original Spanish:** (empty)

**🆕 LLM Generated:** En un ejemplo de la complejidad que implica la elaboración de tales regulaciones, en 2018 el Parlamento Europeo aprobó una normativa sobre IA que algunos han llamado «el derecho a la explicación». Est...

**Confidence:** 0.05

---

### Issue 76 ✅ FIXED

**English:** I believe that regulation of AI should be modeled on the regulation of other technologies, particularly those in biological and medical sciences, such as genetic engineering. In those fields, regulati...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Creo que la regulación de la IA debería basarse en la regulación de otras tecnologías, especialmente las de ciencias biológicas y médicas, como la ingeniería genética. En esos campos, la regulación —c...

**Confidence:** 0.05

---

### Issue 77 ✅ FIXED

**English:** This infrastructure is just beginning to be formed. In the United States, state governments are starting to look into creating regulations, such as those for face recognition or self-driving vehicles....

**Original Spanish:** (empty)

**🆕 LLM Generated:** Esta infraestructura apenas está comenzando a formarse. En los Estados Unidos, los gobiernos estatales están starting a investigar la creación de regulaciones, como aquellas relacionadas con el recono...

**Confidence:** 0.05

---

### Issue 78 ✅ FIXED

**English:** A number of nonprofit think tanks have cropped up to fill the void, often funded by wealthy tech entrepreneurs who are worried about AI. These organizations—with names such as Future of Humanity Insti...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Un número creciente de think tanks sin fines de lucro han surgido para llenar el vacío, a menudo financiados por emprendedores tecnológicos adinerados que están preocupados por la IA. Estas organizaci...

**Confidence:** 0.05

---

### Issue 79 ✅ FIXED

**English:** One stumbling block is that there is no general agreement in the field on what the priorities for developing regulation and ethics should be. Should the immediate focus be on algorithms that can expla...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Uno de los principales obstáculos es que no existe un acuerdo general en el campo sobre cuáles deberían ser las prioridades para desarrollar regulaciones y ética. ¿Debe la atención inmediata centrarse...

**Confidence:** 0.05

---

### Issue 80 ✅ FIXED

**English:** So far, my discussion has focused on ethical issues of how humans use AI. But there’s another important question: Could machines themselves be able to have their own sense of morality, complete enough...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Hasta ahora, mi análisis se ha centrado en las cuestiones éticas sobre cómo los humanos utilizamos la IA. Pero hay otra pregunta importante: ¿Podrían las máquinas tener su propio sentido de moralidad,...

**Confidence:** 0.05

---

### Issue 81 ✅ FIXED

**English:** People have been thinking about “machine morality” for as long as they’ve been thinking about AI.14 Probably the best-known discussion of machine morality comes from Isaac Asimov’s science fiction sto...

**Original Spanish:** (empty)

**🆕 LLM Generated:** La gente ha reflexionado sobre la "moralidad de las máquinas" desde que empezó a hacerlo sobre la IA. La discusión más conocida sobre este tema proviene de los cuentos de ciencia ficción de Isaac Asim...

**Confidence:** 0.05

---

### Issue 82 ✅ FIXED

**English:** 1.  A robot may not injure a human being, or, through inaction, allow a human being to come to harm.

**Original Spanish:** (empty)

**🆕 LLM Generated:** Un robot no debe dañar a un ser humano ni, por omisión, permitir que un ser humano sufra algún mal. ±

**Confidence:** 0.05

---

### Issue 83 ✅ FIXED

**English:** 2.  A robot must obey the orders given to it by human beings except where such orders would conflict with the First Law.

**Original Spanish:** (empty)

**🆕 LLM Generated:** Un robot debe obedecer las órdenes que le dan los seres humanos, excepto en aquellos casos en que tales órdenes entren en conflicto con la Primera Ley. ±

**Confidence:** 0.05

---

### Issue 84 ✅ FIXED

**English:** 3.  A robot must protect its own existence, as long as such protection does not conflict with the First or Second Law.15

**Original Spanish:** (empty)

**🆕 LLM Generated:** Un robot debe proteger su propia existencia, siempre y cuando tal protección no entre en conflicto con la Primera o Segunda Ley. ±

**Confidence:** 0.05

---

### Issue 85 ✅ FIXED

**English:** These laws have become famous, but in truth, Asimov’s purpose was to show how such a set of rules would inevitably fail. “Runaround,” the 1942 story in which Asimov first introduced these laws, featur...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Estas leyes han adquirido fama, pero en realidad, el propósito de Asimov era mostrar cómo un conjunto así de normas fracasaría inevitablemente. "Runaround", la historia de 1942 en la que Asimov presen...

**Confidence:** 0.05

---

### Issue 86 ✅ FIXED

**English:** The science fiction writer Arthur C. Clarke used a similar plot device in his 1968 book, 2001: A Space Odyssey.16 The artificially intelligent computer HAL is programmed to always be truthful to human...

**Original Spanish:** (empty)

**🆕 LLM Generated:** El escritor de ciencia ficción Arthur C. Clarke empleó un dispositivo argumental similar en su libro de 1968, Odisea del espacio 2001. La computadora con inteligencia artificial HAL está programada pa...

**Confidence:** 0.05

---

### Issue 87 ✅ FIXED

**English:** Wiener’s comment captures what is called the value alignment problem in AI: the challenge for AI programmers to ensure that their systems’ values align with those of humans. But what are the values of...

**Original Spanish:** (empty)

**🆕 LLM Generated:** El comentario de Wiener plantea el problema conocido como el desafío del alineamiento de valores en la IA: la tarea que enfrentan los programadores de IA para asegurar que los valores de sus sistemas ...

**Confidence:** 0.05

---

### Issue 88 ✅ FIXED

**English:** Welcome to Moral Philosophy 101. We’ll start with every moral philosophy student’s favorite thought experiment, the trolley problem: You are driving a speeding trolley down a set of tracks, and just a...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Bienvenidos a Filosofía Moral 101. Comenzaremos con el experimento mental favorito de todo estudiante de filosofía moral, el problema del tren: Está conduciendo un tren a gran velocidad por unos riele...

**Confidence:** 0.05

---

### Issue 89 ✅ FIXED

**English:** The trolley problem has been a staple of undergraduate ethics classes for the last century. Most people answer that it would be morally preferable for the driver to steer onto the spur, killing the si...

**Original Spanish:** (empty)

**🆕 LLM Generated:** El problema del tranvía ha sido un Classicismo en clases de ética universitaria durante el último siglo. La mayoría de la gente responde que sería moralmente preferible para el conductor desviarse hac...

**Confidence:** 0.05

---

### Issue 90 ✅ FIXED

**English:** The trolley problem has recently reemerged as part of the media’s coverage of self-driving cars,20 and the question of how an autonomous vehicle should be programmed to deal with such problems has bec...

**Original Spanish:** (empty)

**🆕 LLM Generated:** El problema del tranvía ha vuelto recientemente a la luz como parte de la cobertura mediática de los vehículos autónomos, y la cuestión de cómo se debe programar un vehículo autónomo para afrontar ese...

**Confidence:** 0.05

---

### Issue 91 ✅ FIXED

**English:** In 2016, three researchers published results from surveys of several hundred people who were given trolley-problem-like scenarios that involved self-driving cars, and were asked for their views of the...

**Original Spanish:** (empty)

**🆕 LLM Generated:** En 2016, tres investigadores publicaron los resultados de encuestas a varias cientos de personas a quienes se les presentaron situaciones similares al problema del tranvía que involucraban coches autó...

**Confidence:** 0.05

---

### Issue 92 ✅ FIXED

**English:** Some AI ethics researchers have suggested that we give up trying to directly program moral rules for machines, and instead have machines learn moral values on their own by observing human behavior.23 ...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Algunos investigadores de ética de la IA han propuesto que abandonemos el intento de programar directamente reglas morales para las máquinas y, en su lugar, permitamos que las máquinas aprendan valore...

**Confidence:** 0.05

---

### Issue 93 ✅ FIXED

**English:** To my mind, progress on giving computers moral intelligence cannot be separated from progress on other kinds of intelligence: the true challenge is to create machines that can actually understand the ...

**Original Spanish:** (empty)

**🆕 LLM Generated:** A mi juicio, el progreso en dotación de inteligencia moral a los ordenadores no puede separarse del progreso en otros tipos de inteligencia: el reto verdadero consiste en crear máquinas que puedan ent...

**Confidence:** 0.05

---

### Issue 94 ✅ FIXED

**English:** So far in this book we’ve seen how deep neural networks, trained on enormous data sets, can rival the visual abilities of humans in particular tasks. We’ve also seen some of the weaknesses of these ne...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Hasta ahora en este libro hemos visto cómo las redes neuronales profundas, entrenadas en conjuntos de datos inmensos, pueden rivalizar con las habilidades visuales humanas en tareas concretas. También...

**Confidence:** 0.05

---

### Issue 95 ✅ FIXED

**English:** Figure 23 illustrates a hypothetical learning episode. The episode begins with the trainer (me) placing Rosie and the ball in some initial locations on the field, with Rosie facing the ball (figure 23...

**Original Spanish:** Figura 23. Un hipotético primer episodio de aprendizaje por refuerzo.

**🔍 Vector Search (0.96):** La figura 23 ilustra un episodio hipotético de aprendizaje. El episodio comienza con el entrenador (yo) colocando a Rosie y el balón en determinadas posiciones iniciales en el campo, con Rosie de fren...

**Confidence:** 0.3764849305152893

---

### Issue 96 ✅ FIXED

**English:** The Most Challenging of Domains

**Original Spanish:** (empty)

**🆕 LLM Generated:** El Dominio Más Difícil ±

**Confidence:** 0.05

---

### Issue 97 ✅ FIXED

**English:** One additional aspect of DeepMind’s statement needs to be explored: “even in the most challenging of domains.” How can we assess how challenging a domain is for AI? As we’ve seen, many things we human...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Uno de los aspectos adicionales del comunicado de DeepMind que merece ser examinado es: "incluso en los dominios más desafiantes". ¿Cómo podemos evaluar la dificultad de un dominio para la IA? Como he...

**Confidence:** 0.05

---

### Issue 98 ✅ FIXED

**English:** One way to assess the challenge of a domain for computers is to see how well very simple algorithms perform on it. In 2018, a group of researchers at Uber AI Labs found that some relatively simple alg...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Una forma de evaluar el desafío de un dominio para las computadoras es observar cómo se desempeñan los algoritmos muy simples en él. En 2018, un grupo de investigadores en Uber AI Labs descubrió que a...

**Confidence:** 0.05

---

### Issue 99 ✅ FIXED

**English:** You’d think that a network with random weights would perform abominably on an Atari video game. Indeed, most such networks are terrible players. But the Uber researchers kept trying new random-weight ...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Se podría pensar que una red con pesos aleatorios desempeñaría horriblemente en un juego de video de Atari. En efecto, la mayoría de tales redes son malísimas jugadoras. Pero los investigadores de Ube...

**Confidence:** 0.05

---

### Issue 100 ✅ FIXED

**English:** I haven’t heard of anyone trying a similar random search for network weights for Go. I’d be very surprised if that worked at all. Given the long history of attempts to build computer Go players, I’m c...

**Original Spanish:** (empty)

**🆕 LLM Generated:** No he oído hablar de nadie que haya intentado una búsqueda aleatoria similar para los pesos de la red en Go. Me sorprendería mucho si eso funcionara en absoluto. Dada la larga historia de intentos de ...

**Confidence:** 0.05

---

### Issue 101 ✅ FIXED

**English:** Like other applications of deep learning, it’s hard to interpret what the neural networks used in these game-playing systems have actually learned. In reading the sections above, you might have notice...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Al igual que otras aplicaciones del aprendizaje profundo, es difícil interpretar qué es lo que los redes neuronales utilizadas en estos sistemas de juego han aprendido realmente. Al leer las secciones...

**Confidence:** 0.05

---

### Issue 102 ✅ FIXED

**English:** It’s dangerously easy, for me as much as anyone, to slip into this kind of language when talking about the behavior of AI systems. However, our language often carries unconscious assumptions that may ...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Es peligrosamente fácil, para mí tanto como para cualquier otro, caer en este tipo de lenguaje al hablar sobre el comportamiento de los sistemas de IA. Sin embargo, nuestro lenguaje a menudo lleva sup...

**Confidence:** 0.05

---

### Issue 103 ✅ FIXED

**English:** The system has learned no such thing; it doesn’t really understand what a tunnel, or what a wall is; it has just learned specific contingencies for particular scenarios. Transfer tests—in which the de...

**Original Spanish:** (empty)

**🆕 LLM Generated:** El sistema no ha aprendido nada de eso; realmente no entiende lo que es un túnel o una pared; simplemente ha aprendido contingencias específicas para situaciones particulares. Las pruebas de transfere...

**Confidence:** 0.05

---

### Issue 104 ✅ FIXED

**English:** Marcus is referring to a few studies that tried to probe how well deep Q-learning systems can transfer what they learned, even to very small variations of the same game. For example, one group of rese...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Marcus se refiere a unos pocos estudios que intentaron explorar hasta qué punto los sistemas de aprendizaje profundo Q puedentransferir lo aprendido, incluso a pequeñas variaciones del mismo juego. Po...

**Confidence:** 0.05

---

### Issue 105 ✅ FIXED

**English:** These are just two examples of deep Q-learning’s inability to generalize, which contrasts strikingly with human intelligence. I don’t know of any study that probed the concept of tunneling in DeepMind...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Estos son solo dos ejemplos de la incapacidad de Q-learning profundo para generalizar, lo cual contrasta marcadamente con la inteligencia humana. No conozco ningún estudio que haya explorado el concep...

**Confidence:** 0.05

---

### Issue 106 ✅ FIXED

**English:** These demonstrations make clear that it is misleading to credit deep reinforcement learning with inducing concepts like wall or paddle; rather, such remarks are what comparative (animal) psychology so...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Estas manifestaciones dejan claro que es engañoso atribuir a la aprendizaje reforzado profundo el mérito de inducir conceptos como la pared o la pala; más bien, tales afirmaciones son lo que la psicol...

**Confidence:** 0.05

---

### Issue 107 ✅ FIXED

**English:** Similarly, while AlphaGo exhibited miraculous “intuition” in playing Go, the system doesn’t have any mechanisms, as far as I can tell, that would allow it to generalize its Go-playing abilities, even ...

**Original Spanish:** (empty)

**🆕 LLM Generated:** De manera similar, mientras AlphaGo exhibió una "intuición" milagrosa en el juego de Go, no parece tener mecanismos que le permitan generalizar sus habilidades en el juego de Go, ni siquiera a un tabl...

**Confidence:** 0.05

---

### Issue 108 ✅ FIXED

**English:** In short, while these deep Q-learning systems have achieved superhuman performance in some narrow domains, and even exhibit what resembles “intuition” in these domains, they are lacking something abso...

**Original Spanish:** (empty)

**🆕 LLM Generated:** En resumen, mientras estos sistemas profundos de aprendizaje por reforzamiento han logrado un rendimiento superhumano en algunos dominios estrechos y hasta exhiben lo que se asemeja a una "intuición" ...

**Confidence:** 0.05

---

### Issue 109 ✅ FIXED

**English:** There’s another reason to suspect that these systems are not learning humanlike concepts or understanding their domains in the way humans do: like supervised-learning systems, these deep Q-learning sy...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Hay otro motivo para sospechar que estos sistemas no están aprendiendo conceptos humanos ni comprendiendo sus dominios de la manera en que lo hacen los seres humanos: al igual que los sistemas de apre...

**Confidence:** 0.05

---

### Issue 110 ✅ FIXED

**English:** Here’s something we must keep in mind when thinking about games like chess and Go and their relation to human intelligence. Consider the reasons many parents encourage their kids to join the school ch...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Aquí hay algo que debemos tener en cuenta al reflexionar sobre juegos como el ajedrez y el Go y su relación con la inteligencia humana. Consideren las razones por las que muchos padres animan a sus hi...

**Confidence:** 0.05

---

### Issue 111 ✅ FIXED

**English:** But AlphaGo, in spite of the millions of games it has played during its training, has not learned to “think” better about anything except the game of Go. In fact, it has no ability to think about anyt...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Pero a pesar de los millones de partidas que ha jugado durante su entrenamiento, AlphaGo no ha aprendido a "pensar" mejor sobre nada excepto el juego de Go. De hecho, no tiene capacidad para pensar en...

**Confidence:** 0.05

---

### Issue 112 ✅ FIXED

**English:** It’s certainly true that the deep Q-learning method used in AlphaGo can be used to learn other tasks, but the system itself would have to be wholly retrained; it would have to start essentially from s...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Es cierto que el método de aprendizaje profundo utilizado en AlphaGo podría aplicarse para aprender otras tareas, pero el sistema en sí tendría que ser entrenado completamente de nuevo; debería comenz...

**Confidence:** 0.05

---

### Issue 113 ✅ FIXED

**English:** This brings us back to the “easy things are hard” paradox of AI. AlphaGo was a great achievement for AI; learning largely via self-play, it was able to definitively defeat one of the world’s best huma...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Esto nos lleva de vuelta al paradoxo "lo fácil es difícil" de la IA. AlphaGo fue un gran logro para la IA; aprendiendo principalmente mediante el juego propio, pudo derrotar definitivamente a uno de l...

**Confidence:** 0.05

---

### Issue 114 ✅ FIXED

**English:** Finally, let’s consider Demis Hassabis’s statement that the ultimate goal of these demonstrations on games is to “use them so they apply to real-world problems and have a huge impact on things like he...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Finalmente, démosle un vistazo al comentario de Demis Hassabis de que el objetivo último de estas demostraciones sobre juegos es "usarlas para aplicarlas a problemas del mundo real y tener un gran imp...

**Confidence:** 0.05

---

### Issue 115 ✅ FIXED

**English:** The need for transfer learning is one obstacle. But there are additional reasons that it will be difficult to extend reinforcement learning’s success in games to the real world. Games such as Breakout...

**Original Spanish:** (empty)

**🆕 LLM Generated:** La necesidad de aprendizaje por transferencia es un obstáculo. Sin embargo, hay razones adicionales que dificultarán la extensión del éxito del aprendizaje por refuerzo en los juegos al mundo real. Ju...

**Confidence:** 0.05

---

### Issue 116 ✅ FIXED

**English:** The real world doesn’t come so cleanly delineated. Douglas Hofstadter has pointed out that the very notion of a clearly defined “state” isn’t at all realistic. “If you look at situations in the world,...

**Original Spanish:** (empty)

**🆕 LLM Generated:** El mundo real no se presenta tan claramente definido. Douglas Hofstadter ha señalado que incluso la idea de un estado claramente definido es todo menos realista. "Si miras situaciones en el mundo, no ...

**Confidence:** 0.05

---

### Issue 117 ✅ FIXED

**English:** As an example, consider using reinforcement learning to train a robot to perform a very useful real-world task: take the dirty dishes stacked in the sink and put them in the dishwasher. (Oh, the harmo...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Como ejemplo, consideremos utilizar aprendizaje por refuerzo para entrenar a un robot con el fin de que realice una tarea muy útil en el mundo real: tomar los platos sucios apilados en el fregadero y ...

**Confidence:** 0.05

---

### Issue 118 ✅ FIXED

**English:** DeepMind’s game-playing agents required millions of iterations of training. If we don’t want millions of broken dishes, we’d have to train our robot in simulation. Games are very fast and accurate to ...

**Original Spanish:** (empty)

**🆕 LLM Generated:** El agente de DeepMind requería millones de iteraciones de entrenamiento. Si no queremos millones de platos rotos, tendríamos que entrenar a nuestro robot en simulación. Los juegos son muy rápidos y pr...

**Confidence:** 0.05

---

### Issue 119 ✅ FIXED

**English:** All these issues led Andrej Karpathy, Tesla’s director of AI, to note that, for real-world tasks like this, “basically every single assumption that Go satisfies and that AlphaGo takes advantage of are...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Todos estos problemas llevaron a Andrej Karpathy, director de IA de Tesla, a señalar que, para tareas del mundo real como ésta, "casi todas las suposiciones que Go cumple y que AlphaGo aprovecha son v...

**Confidence:** 0.05

---

### Issue 120 ✅ FIXED

**English:** No one knows what that successful approach would be. Indeed, the field of deep reinforcement learning is still quite young. The results I described in this chapter can be seen as a proof of principle:...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Nadie sabe cuál sería ese exitoso enfoque. De hecho, el campo del aprendizaje reforzado profundo aún es bastante joven. Los resultados que he descrito en este capítulo pueden verse como una prueba de ...

**Confidence:** 0.05

---

### Issue 121 ✅ FIXED

**English:** Words, and the Company They Keep

**Original Spanish:** (empty)

**🆕 LLM Generated:** Palabras, y la Compañía que Mantienen ±

**Confidence:** 0.05

---

### Issue 122 ✅ FIXED

**English:** Figure 38 gives a sketch of what’s under the hood when you use Google Translate (and other contemporary machine-translation programs), here translating from English to French.3 It’s a complicated syst...

**Original Spanish:** Figura 38. Esquema de un par de redes «codificador-descodificador» para la traducción de idiomas. Los rectángulos blancos representan las redes codificadora y descodificadora, que operan en pasos temp...

**🔍 Vector Search (0.88):** En la figura 38 (en la página siguiente) se muestra un esbozo de lo que ocurre cuando se utiliza Google Translate (y otros programas actuales de traducción automática) para traducir del inglés al fran...

**Confidence:** 0.3891383409500122

---

### Issue 123 ✅ FIXED

**English:** Figure 39 gives a sketch of how the Show and Tell system works.25 It’s something like the encoder-decoder system from figure 38, but here the input is an image instead of a sentence. The image is fed ...

**Original Spanish:** Figura 39. Esquema del sistema automatizado de subtitulación de imágenes de Google.

**🔍 Vector Search (0.92):** La figura 39 muestra de forma esquemática el funcionamiento del sistema Show and Tell.[274] Es parecido al sistema codificador-descodificador de la figura 38 (en la página 252), pero aquí la entrada e...

**Confidence:** 0.3366542458534241

---

### Issue 124 ✅ FIXED

**English:** A man went to a restaurant and ordered a burger, cooked sparse. When it arrived, it was burnt for an almond brittle. The waitress stopped near the man’s table. “Is the burger okay?” she asked. “Oh, it...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Un hombre fue a un restaurante y pidió una hamburguesa, cocinada con escasez de ingredientes. Cuando llegó, estaba quemada como un brittle de almendras. La mesera se detuvo cerca de la mesa del hombre...

**Confidence:** 0.05

---

### Issue 125 ✅ FIXED

**English:** A man walked into a restaurant and ordered a rarely seen hamburger. When it reached its destination, it was roasted very crispy. The waitress stopped next to the man’s table. “Is the hamburger good?” ...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Un hombre entró en un restaurante y ordenó un hamburguesa que apenas se ve hoy en día. Cuando llegó a su mesa, estaba muy crujiente. La mesera se detuvo junto a la mesa del hombre. "¿La hamburguesa es...

**Confidence:** 0.05

---

### Issue 126 ✅ FIXED

**English:** (A list of names is displayed.)

**Original Spanish:** (empty)

**🆕 LLM Generated:** (Cada uno de los nombres se muestra en una lista.)

NOTE: The translation provided maintains the original structure and style, using "Cada uno de los nombres se muestra en una lista" to convey the sam...

**Confidence:** 0.05

---

### Issue 127 ✅ FIXED

**English:** Similarly, we conceptualize emotional states such as happiness and sadness as physical directions—up and down. I might be “feeling down” and could “fall into a depression.” My mood might be “quickly d...

**Original Spanish:** (empty)

**🆕 LLM Generated:** De manera similar, concebimos estados emocionales como la felicidad y la tristeza como direcciones físicas - arriba y abajo. Es posible que "me sienta bajo de ánimos" y que "caiga en una depresión". M...

**Confidence:** 0.05

---

### Issue 128 ✅ FIXED

**English:** Going further, we often conceptualize social interactions in terms of physical temperature. “I was given a warm welcome.” “She gave me an icy stare.” “He gave me the cold shoulder.” Such phrasings are...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Al avanzar, a menudo conceptualizamos las interacciones sociales en términos de temperatura física. "Me dieron una cálida bienvenida". "Ella me lanzó una mirada helada". "Él me dio la espalda fría". T...

**Confidence:** 0.05

---

### Issue 129 ✅ FIXED

**English:** Psychologists have probed these ideas in many fascinating experiments. One group of researchers noted that the same brain area seems to be activated whether a person thinks about physical warmth or so...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Psicólogos han explorado estas ideas en muchos experimentos fascinantes. Un grupo de investigadores observó que la misma área del cerebro parece activarse tanto si una persona piensa en el calor físic...

**Confidence:** 0.05

---

### Issue 130 ✅ FIXED

**English:** Other researchers have found similar results. Moreover, the reverse of this connection between physical and social “temperature” also seems to hold: other groups of psychologists found that “warm” or ...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Otros investigadores han hallado resultados similares. Además, la inversa de esta conexión entre la temperatura física y social también parece aplicar: otros grupos de psicólogos descubrieron que las ...

**Confidence:** 0.05

---

### Issue 131 ✅ FIXED

**English:** While these experiments and interpretations are still controversial in the psychology community, the results can be interpreted as supporting the claims of Barsalou and of Lakoff and Johnson: we under...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Mientras estas experiencias e interpretaciones siguen siendo controvertidas en la comunidad psicológica, los resultados pueden interpretarse como sosteniendo las afirmaciones de Barsalou y de Lakoff y...

**Confidence:** 0.05

---

### Issue 132 ✅ FIXED

**English:** It’s hard to talk about understanding without talking about consciousness. When I started writing this book, I planned to entirely sidestep the question of consciousness, because it is so fraught scie...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Es difícil hablar de comprensión sin hablar de conciencia. Cuando comencé a escribir este libro, tenía la intención de evitar por completo la pregunta de la conciencia, porque es tan problemática desd...

**Confidence:** 0.05

---

### Issue 133 ✅ FIXED

**English:** So far I’ve described several ideas from psychology about the core “intuitive” knowledge humans are born with or acquire early in life, and how this core knowledge underlies the mental models that for...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Hasta ahora he descrito varias ideas de la psicología sobre el conocimiento "intuitivo" básico con el que los seres humanos nacen o adquieren tempranamente en la vida, y cómo este conocimiento básico ...

**Confidence:** 0.05

---

### Issue 134 ✅ FIXED

**English:** Abstraction is the ability to recognize specific concepts and situations as instances of a more general category. Let’s make the idea of abstraction more concrete (pun intended!). Imagine that you are...

**Original Spanish:** (empty)

**🆕 LLM Generated:** La abstracción es la capacidad de reconocer conceptos y situaciones específicos como instancias de una categoría más general. Hagamos que la idea de abstracción sea más concreta (¡con el juego de pala...

**Confidence:** 0.05

---

### Issue 135 ✅ FIXED

**English:** Three months: S can distinguish among facial expressions depicting happiness and sadness, generalizing across the different people she interacts with. She has abstracted the concepts of a happy face a...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Tres meses: S puede distinguir entre expresiones faciales que representan felicidad y tristeza, generalizando en diferentes personas con las que interactúa. Ha abstraído los conceptos de una cara feli...

**Confidence:** 0.05

---

### Issue 136 ✅ FIXED

**English:** Six months: S can now recognize when people “wave bye-bye” to her, and she can wave back. She has abstracted the visual concept of waving, has learned how to respond with the “same” gesture.

**Original Spanish:** (empty)

**🆕 LLM Generated:** Seis meses: Ahora S puede reconocer cuando la gente "adiós con la mano" y puede devolvérsela. Ha abstraído el concepto visual de saludar con la mano y ha aprendido cómo responder con el mismo gesto. ±

**Confidence:** 0.05

---

### Issue 137 ✅ FIXED

**English:** Eighteen months: S has abstracted the concepts of cat and dog (as well as many other categories) so that she is able to recognize different examples of cats and dogs in photographs, drawings, and cart...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Dieciocho meses: S ha abstraído los conceptos de gato y perro (así como muchas otras categorías), por lo que es capaz de reconocer diferentes ejemplos de gatos y perros en fotografías, dibujos y caric...

**Confidence:** 0.05

---

### Issue 138 ✅ FIXED

**English:** Age three: S recognizes individual letters of the alphabet in different people’s handwriting and in printed fonts. In addition, she can distinguish between lower- and uppercase letters. Her abstractio...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Tres años: S reconoce las letras individuales del alfabeto en diferentes escrituras de personas y en fuentes impresas. Además, puede distinguir entre mayúsculas y minúsculas. Sus abstracciones de conc...

**Confidence:** 0.05

---

### Issue 139 ✅ FIXED

**English:** Age eight: I overheard S’s best friend, J, telling S about the time J’s mother forgot to pick her up after her soccer game. S replied, “Oh, yeah, the exact same thing happened to me. I bet you were ma...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Edad ocho: oí a J, la mejor amiga de S, contándole a S sobre el día en que su madre se olvidó de recogerla después del partido de fútbol. S respondió: “Ah, sí, justo lo mismo me pasó a mí. Seguro que ...

**Confidence:** 0.05

---

### Issue 140 ✅ FIXED

**English:** Age thirteen: S is becoming a rebellious teenager. I have repeatedly requested that she clean up her room. Today she yelled back to me, “You can’t make me; Abraham Lincoln freed the slaves!” I was ann...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Age trece: S se está convirtiendo en una adolescente rebelde. Le he pedido repetidamente que limpie su habitación. Hoy gritó en respuesta: “¡No puedes obligarme a hacerlo; Abraham Lincoln liberó a los...

**Confidence:** 0.05

---

### Issue 141 ✅ FIXED

**English:** Age sixteen: S’s interest in music is growing. The two of us like to play a game in the car: we turn on a classical music station in the middle of a piece and see which of us can most quickly figure o...

**Original Spanish:** (empty)

**🆕 LLM Generated:** A los dieciséis años, el interés de S por la música está en aumento. Los dos nos gusta jugar un juego en el coche: encendemos una estación de radio de música clásica en medio de una pieza y vemos cuál...

**Confidence:** 0.05

---

### Issue 142 ✅ FIXED

**English:** Age twenty: S sent me a long email message about her life at college. She described her week as “a study-a-thon, followed by an eat-a-thon and a sleep-a-thon.” She said that college is turning her int...

**Original Spanish:** (empty)

**🆕 LLM Generated:** A los veinte años, S me envió un correo electrónico muy largo sobre su vida en la universidad. Describió su semana como «un estudio-a-thón seguido de un comida-a-thón y un dormir-a-thón». Dijo que la ...

**Confidence:** 0.05

---

### Issue 143 ✅ FIXED

**English:** Age twenty-six: S has graduated from law school and was hired by a prestigious firm. Her most recent client (the defendant) is an internet company that provides a public “blogging” platform. The compa...

**Original Spanish:** (empty)

**🆕 LLM Generated:** A los veintiséis años, S había graduado de la escuela de derecho y fue contratada por un despacho prestigiousmo. Su último cliente (el acusado) es una compañía de internet que proporciona una platafor...

**Confidence:** 0.05

---

### Issue 144 ✅ FIXED

**English:** The purpose of my foray into imaginary parent journaling was to make some important points about abstraction and analogy. Abstraction, in some form, underlies all of our concepts, even from earliest i...

**Original Spanish:** (empty)

**🆕 LLM Generated:** El objetivo de mi incursión en la bitácora imaginaria fue hacer algunos puntos importantes sobre la abstracción y la analogía. La abstracción, bajo alguna forma, subyace a todas nuestras concepciones,...

**Confidence:** 0.05

---

### Issue 145 ✅ FIXED

**English:** Abstraction is closely linked to analogy making. Douglas Hofstadter, who has studied abstraction and analogy making for several decades, defines analogy making in a very general sense as “the percepti...

**Original Spanish:** (empty)

**🆕 LLM Generated:** La abstracción está estrechamente ligada a la creación de analogías. Douglas Hofstadter, quien ha estudiado la abstracción y la creación de analogías durante varias décadas, define la creación de anal...

**Confidence:** 0.05

---

### Issue 146 ✅ FIXED

**English:** In short, analogies, most often made unconsciously, are what underlie our abstraction abilities and the formation of concepts. As Hofstadter and his coauthor, the psychologist Emmanuel Sander, stated,...

**Original Spanish:** (empty)

**🆕 LLM Generated:** En resumen, las analogías, que se suelen hacer de manera inconsciente, son el fundamento de nuestras habilidades abstraccionales y la formación de conceptos. Como dice Hofstadter junto a su coautor, e...

**Confidence:** 0.05

---

### Issue 147 ✅ FIXED

**English:** In this chapter, I have sketched some ideas from recent work in psychology regarding the mental mechanisms by which humans understand and act appropriately in the situations they encounter. We have co...

**Original Spanish:** (empty)

**🆕 LLM Generated:** En este capítulo, he esbozado algunas ideas de trabajos recientes en psicología sobre los mecanismos mentales mediante los cuales los seres humanos comprenden y actúan adecuadamente en las situaciones...

**Confidence:** 0.05

---

### Issue 148 ✅ FIXED

**English:** I certainly don’t claim to have covered all of the components of human understanding. Indeed, many people have noted that the terms understanding and meaning (not to mention consciousness) are merely ...

**Original Spanish:** (empty)

**🆕 LLM Generated:** No puedo asegurar que haya abordado todos los aspectos de la comprensión humana. De hecho, muchos han señalado que los términos comprensión y significado (y no hablemos de conciencia) son meras palabr...

**Confidence:** 0.05

---

### Issue 149 ✅ FIXED

**English:** Until recently, the question of what mental mechanisms allow people to understand the world—and whether machines could have such understanding as well—was almost exclusively the province of philosophe...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Hasta hace poco, la pregunta de qué mecanismos mentales permiten a las personas entender el mundo —y si las máquinas podrían tener una comprensión similar— era casi exclusivamente el dominio de filóso...

**Confidence:** 0.05

---

### Issue 150 ✅ FIXED

**English:** Each problem features twelve boxes: six on the left and six on the right. The six left-hand boxes in each problem exemplify the “same” concept, the six right-hand boxes exemplify a related concept, an...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Cada problema presenta doce cajas: seis a la izquierda y seis a la derecha. Las seis cajas de la izquierda en cada problema ejemplifican el "mismo" concepto, las seis cajas de la derecha exemplifican ...

**Confidence:** 0.05

---

### Issue 151 ✅ FIXED

**English:** The problems in figure 45 are relatively easy to solve. In fact, Bongard arranged his hundred problems roughly in order of their presumed difficulty. For your enjoyment, figure 46 gives six additional...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Los problemas de la figura 45 son relativamente fáciles de resolver. De hecho, Bongard ordenó sus cien problemas más o menos según su dificultad presumida. Para su entretenimiento, la figura 46 ofrece...

**Confidence:** 0.05

---

### Issue 152 ✅ FIXED

**English:** Bongard carefully designed these puzzles so that their solution requires some of the same abstraction and analogy-making abilities that a human or AI system needs in the real world. In a Bongard probl...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Bongard diseñó cuidadosamente estos acertijos para que su solución requiera cierta abstracción y habilidad para hacer analogías, habilidades que un ser humano o un sistema de IA necesita en el mundo r...

**Confidence:** 0.05

---

### Issue 153 ✅ FIXED

**English:** To discover this subtle sameness, you need to determine which attributes of the situation are relevant and which you can ignore. In problem 2 (figure 45), it doesn’t matter whether a shape is black or...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Para descubrir esta sutileza compartida, debes determinar cuáles atributos de la situación son relevantes y cuáles puedes ignorar. En el problema 2 (figura 45), no importa si una forma es negra o blan...

**Confidence:** 0.05

---

### Issue 154 ✅ FIXED

**English:** To make things even harder for machines, the relevant concepts can be encoded in an abstract, hard-to-perceive way, such as the concepts three and four in problem 91. In some problems, it might not be...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Para dificultar aún más las cosas para las máquinas, los conceptos relevantes pueden ser codificados de una manera abstracta y difícil de percibir, como los conceptos tres y cuatro en el problema 91. ...

**Confidence:** 0.05

---

### Issue 155 ✅ FIXED

**English:** Bongard problems also challenge one’s ability to perceive new concepts on the fly. Problem 18 is a good example. The concept common to the boxes on the left is not easy to verbalize; it’s something li...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Los problemas de Bongard también desafían la capacidad humana para percibir nuevos conceptos sobre la marcha. El problema 18 es un buen ejemplo. La idea común a las cajas de la izquierda no es fácil d...

**Confidence:** 0.05

---

### Issue 156 ✅ FIXED

**English:** Bongard’s book, published in English in 1970, was rather obscure, and initially few people knew of its existence. However, Douglas Hofstadter, who had come upon the book in 1975, was deeply impressed ...

**Original Spanish:** (empty)

**🆕 LLM Generated:** El libro de Bongard, publicado en inglés en 1970, era bastante desconocido y initially few people knew of its existence. However, Douglas Hofstadter, who had come upon the book in 1975, was deeply imp...

**Confidence:** 0.05

---

### Issue 157 ✅ FIXED

**English:** Since childhood, I’ve always loved puzzles, especially ones involving logic or patterns; when I read GEB, I was particularly enchanted by Bongard problems. I was also intrigued by Hofstadter’s ideas, ...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Desde mi infancia, siempre he amado los rompecabezas, especialmente aquellos que involucraban lógica o patrones; cuando leí GEB, quedé particularmente cautivado por los problemas de Bongard. También m...

**Confidence:** 0.05

---

### Issue 158 ✅ FIXED

**English:** Many other people have been equally enchanted by Bongard problems, and several researchers have created AI programs that attempt to solve them. Most of these programs make simplifying assumptions (for...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Muchas otras personas han quedado igualmente cautivadas por los problemas de Bongard y varios investigadores han creado programas de IA que intentan resolverlos. La mayoría de estos programas hacen su...

**Confidence:** 0.05

---

### Issue 159 ✅ FIXED

**English:** What about convolutional neural networks? Given that they have performed so spectacularly on object classification (for example, in the huge ImageNet Visual Recognition Challenge that I described in c...

**Original Spanish:** (empty)

**🆕 LLM Generated:** ¿Qué pasa con las redes neuronales convolucionales? Dado que han funcionado de manera espectacular en la clasificación de objetos (por ejemplo, en el enorme Desafío de Reconocimiento Visual ImageNet q...

**Confidence:** 0.05

---

### Issue 160 ✅ FIXED

**English:** FIGURE 47: An illustration of how a Bongard problem could be framed as a classification problem, with twelve training examples and a new “test” example

**Original Spanish:** (empty)

**🆕 LLM Generated:** Figura 47: Una ilustración de cómo un problema de Bongard podría enmarcarse como un problema de clasificación, con doce ejemplos de entrenamiento y un nuevo ejemplo de "prueba" ±

**Confidence:** 0.05

---

### Issue 161 ✅ FIXED

**English:** An immediate obstacle is that a set of twelve training examples is laughably inadequate for training a ConvNet; even twelve hundred might not be sufficient. Of course, this is part of Bongard’s point:...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Un obstáculo inmediato es que un conjunto de doce ejemplos de entrenamiento es ridículamente insuficiente para entrenar una red convolucional; incluso docecientos pueden no ser suficientes. Por supues...

**Confidence:** 0.05

---

### Issue 162 ✅ FIXED

**English:** Active Symbols and Analogy Making

**Original Spanish:** (empty)

**🆕 LLM Generated:** Símbolos Activos y Hacer Analogías ±

**Confidence:** 0.05

---

### Issue 163 ✅ FIXED

**English:** After reading Gödel, Escher, Bach and deciding to pursue research in AI, I sought out Douglas Hofstadter, with the hope that I could work on something like Bongard problems. Happily, after some persis...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Después de leer "Gödel, Escher, Bach" y decidir investigar en Inteligencia Artificial, busqué a Douglas Hofstadter con la esperanza de trabajar en algo como los problemas de Bongard. Afortunadamente, ...

**Confidence:** 0.05

---

### Issue 164 ✅ FIXED

**English:** PROBLEM 1: Suppose that the string of letters abc changes to abd. How would you change the string pqrs in the “same way”?

**Original Spanish:** (empty)

**🆕 LLM Generated:** Problema 1: Supongamos que la cadena de letras "abc" cambia a "abd". ¿Cómo cambiarías la cadena "pqrs" de la "misma manera"? ±

**Confidence:** 0.05

---

### Issue 165 ✅ FIXED

**English:** Most people answer pqrt, inferring a rule something like “Replace the rightmost letter by its successor in the alphabet.” Of course, there are other possible rules one could infer, producing different...

**Original Spanish:** (empty)

**🆕 LLM Generated:** La mayoría de la gente responde "pqrt", inferiendo una regla más o menos así: "Reemplaza la letra más a la derecha por su sucesora en el alfabeto". Por supuesto, hay otras posibles reglas que se podrí...

**Confidence:** 0.05

---

### Issue 166 ✅ FIXED

**English:** pqrd: “Replace the rightmost letter by d.”

**Original Spanish:** (empty)

**🆕 LLM Generated:** "Remplaza la letra más a la derecha por una d." ±

**Confidence:** 0.05

---

### Issue 167 ✅ FIXED

**English:** pqrs: “Replace all c’s by d’s. There are no c’s in pqrs, so nothing changes.”

**Original Spanish:** (empty)

**🆕 LLM Generated:** "pqrs: «Reemplaza todas las c por d. No hay ninguna c en pqrs, así que nada cambia.»" ±

**Confidence:** 0.05

---

### Issue 168 ✅ FIXED

**English:** abd: “Replace any string by the string abd.”

**Original Spanish:** (empty)

**🆕 LLM Generated:** "Reemplazar cualquier cadena por la cadena abd." ±

**Confidence:** 0.05

---

### Issue 169 ✅ FIXED

**English:** These alternative answers might seem overly literal-minded, but there’s no strictly logical argument that says they are wrong. In fact, there are infinitely many possible rules one might infer. Why do...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Estas respuestas alternativas podrían parecer excesivamente literales, pero no existe un argumento lógico estricto que afirme que son incorrectas. De hecho, hay innumerables reglas posibles que se pod...

**Confidence:** 0.05

---

### Issue 170 ✅ FIXED

**English:** Here’s another example:

**Original Spanish:** (empty)

**🆕 LLM Generated:** Aquí hay otro ejemplo: ±

**Confidence:** 0.05

---

### Issue 171 ✅ FIXED

**English:** PROBLEM 2: Suppose that the string abc changes to abd. How would you change the string ppqqrrss in the “same way”?

**Original Spanish:** (empty)

**🆕 LLM Generated:** PROBLEM 2: Supongamos que la cadena abc se transforma en abd. ¿Cómo cambiarías la cadena ppqqrrss de "la misma manera"? ±

**Confidence:** 0.05

---

### Issue 172 ✅ FIXED

**English:** Even in this simple alphabetic microworld, sameness can be quite subtle, at least for a machine. In problem 2, a literal application of the rule “replace the rightmost letter by its successor” would y...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Incluso en este mundo microscópico alfabético tan simple, la similitud puede ser bastante sutil, al menos para una máquina. En el problema 2, una aplicación literal de la regla "reemplazar la letra má...

**Confidence:** 0.05

---

### Issue 173 ✅ FIXED

**English:** Problem 2 illustrates, in this microworld, the general notion of conceptual slippage, an idea at the heart of analogy making.19 When you attempt to perceive the essential “sameness” of two different s...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Problema 2 ilustra, en este micromundo, la noción general de desplazamiento conceptual, una idea que se halla en el centro de la creación de analogías.19 Cuando intentas percibir la esencial "semejanz...

**Confidence:** 0.05

---

### Issue 174 ✅ FIXED

**English:** Now consider this problem:

**Original Spanish:** (empty)

**🆕 LLM Generated:** Ahora considera este problema: ±

**Confidence:** 0.05

---

### Issue 175 ✅ FIXED

**English:** PROBLEM 3: Suppose the string abc changes to abd. How would you change the string xyz in the “same way”?

**Original Spanish:** (empty)

**🆕 LLM Generated:** PROBLEM 3: Supongamos que la cadena abc se transforma en abd. ¿Cómo cambiarías la cadena xyz de "la misma manera"? ±

**Confidence:** 0.05

---

### Issue 176 ✅ FIXED

**English:** Most people answer xya, contending that the “successor” of z is a. But suppose that you are a computer program that doesn’t have the concept of a “circular” alphabet, and thus for you the letter z has...

**Original Spanish:** (empty)

**🆕 LLM Generated:** La mayoría de la gente responde xy, sosteniendo que el "sucesor" de z es a. Pero supongamos que eres un programa informático que no tiene el concepto de una "alfabeto circular", por lo que para ti la ...

**Confidence:** 0.05

---

### Issue 177 ✅ FIXED

**English:** The letter-string microworld makes the idea of slippage very visible. In other domains, it can be more subtle. For example, if you look back at Bongard problem 91 in figure 46, in which the shared ess...

**Original Spanish:** (empty)

**🆕 LLM Generated:** El mundo microscópico de la letra-string hace muy visible la idea del deslizamiento. En otros dominios, puede ser más sutil. Por ejemplo, si miramos hacia atrás al problema de Bongard 91 en la figura ...

**Confidence:** 0.05

---

### Issue 178 ✅ FIXED

**English:** Hofstadter envisioned a computer program, called Copycat, that would solve problems like these by using very general algorithms, similar to those he believed humans used when making analogies in any d...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Hofstadter concibió un programa de computadora llamado Copycat que resolvería problemas como estos utilizando algoritmos muy generales, similares a aquellos que creía que los humanos utilizaban al hac...

**Confidence:** 0.05

---

### Issue 179 ✅ FIXED

**English:** When I joined Hofstadter’s research group, my assignment was to work with Hofstadter on developing the Copycat program. As anyone who has made the journey will tell you, the route to a PhD consists ma...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Al unirme al grupo de investigación de Hofstadter, se me asignó trabajar con él en el desarrollo del programa Copycat. Como cualquiera que haya emprendido este camino sabrá, la senda hacia un doctorad...

**Confidence:** 0.05

---

### Issue 180 ✅ FIXED

**English:** Copycat was neither a symbolic, rule-based program nor a neural network, though it included aspects of both symbolic and subsymbolic AI. Copycat solved analogy problems via a continual interaction bet...

**Original Spanish:** (empty)

**🆕 LLM Generated:** "Copycat no era ni un programa simbólico basado en reglas ni una red neural, aunque incluía aspectos de ambos tipos de inteligencia artificial, tanto simbólica como subsimbólica. Copycat resolvía prob...

**Confidence:** 0.05

---

### Issue 181 ✅ FIXED

**English:** PROBLEM 4: If azbzczd changes to abcd, what does pxqxrxsxt change to?

**Original Spanish:** (empty)

**🆕 LLM Generated:** PROBLEMA 4: Si azbzczd se convierte en abcd, ¿qué se convierte pxqxrxsxt en? ±

**Confidence:** 0.05

---

### Issue 182 ✅ FIXED

**English:** PROBLEM 5: If abc changes to abd, what does ace change to?

**Original Spanish:** (empty)

**🆕 LLM Generated:** PROBLEMA 5: Si abc cambia a abd, ¿qué cambio tiene ace? ±

**Confidence:** 0.05

---

### Issue 183 ✅ FIXED

**English:** Both problems require recognizing new concepts on the fly, an ability that Copycat lacked. In problem 4, the z’s and the x’s play the same role, something like “the extra letters that need to be delet...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Ambos problemas exigen reconocer nuevos conceptos sobre la marcha, una habilidad que Care_copy no poseía. En el problema 4, las z's y las x's desempeñan el mismo papel, algo así como "las letras extra...

**Confidence:** 0.05

---

### Issue 184 ✅ FIXED

**English:** Metacognition in the Letter-String World

**Original Spanish:** (empty)

**🆕 LLM Generated:** Metacognición en el mundo de cadenas de letras ±

**Confidence:** 0.05

---

### Issue 185 ✅ FIXED

**English:** An essential aspect of human intelligence—one that isn’t discussed much in AI these days—is the ability to perceive and reflect on one’s own thinking. In psychology, this is called metacognition. Have...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Un aspecto esencial de la inteligencia humana —uno que no se discute mucho en el campo actual de la IA— es la capacidad de percibir y reflexionar sobre su propio pensamiento. En psicología, esto se co...

**Confidence:** 0.05

---

### Issue 186 ✅ FIXED

**English:** James Marshall, at the time a graduate student in Douglas Hofstadter’s research group, took on the project of getting Copycat to reflect on its own “thinking.” He created a program called Metacat, whi...

**Original Spanish:** (empty)

**🆕 LLM Generated:** James Marshall, en ese momento un estudiante de posgrado en el grupo de investigación de Douglas Hofstadter, se hizo cargo del proyecto de hacer que Copycat reflexionara sobre su propio "pensamiento"....

**Confidence:** 0.05

---

### Issue 187 ✅ FIXED

**English:** Recognizing Visual Situations

**Original Spanish:** (empty)

**🆕 LLM Generated:** Reconocer Situaciones Visuales ±

**Confidence:** 0.05

---

### Issue 188 ✅ FIXED

**English:** My own current research is on developing an AI system that uses analogy to flexibly recognize visual situations—visual concepts involving multiple entities and their relationships. For example, each o...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Mi investigación actual se centra en desarrollar un sistema de IA que utiliza la analogía para reconocer visiblemente situaciones visuales—conceptos visuales que implican múltiples entidades y sus rel...

**Confidence:** 0.05

---

### Issue 189 ✅ FIXED

**English:** My collaborators and I are developing a program—called Situate—that combines the object-recognition abilities of deep neural networks with Copycat’s active-symbol architecture, in order to recognize i...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Mis colaboradores y yo estamos desarrollando un programa—llamado Situate—that combina las habilidades de reconocimiento de objetos de redes neuronales profundas con la arquitectura activa de símbolos ...

**Confidence:** 0.05

---

### Issue 190 ✅ FIXED

**English:** Copycat, Metacat, and Situate are only three examples of several analogy-making programs that are based on Hofstadter’s active-symbol architecture.23 Moreover, the active-symbol architecture is only o...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Copión, Metacat y Sitúate son solo tres ejemplos de varias programas de creación de analogías basadas en la arquitectura de símbolos activos de Hofstadter. Además, la arquitectura de símbolos activos ...

**Confidence:** 0.05

---

### Issue 191 ✅ FIXED

**English:** “We Are Really, Really Far Away”

**Original Spanish:** (empty)

**🆕 LLM Generated:** "Estamos Muy, Muy Lejos"

Literary context maintained. ±

**Confidence:** 0.05

---

### Issue 192 ✅ FIXED

**English:** The modern age of artificial intelligence is dominated by deep learning, with its triumvirate of deep neural networks, big data, and ultrafast computers. However, in the quest for robust and general i...

**Original Spanish:** (empty)

**🆕 LLM Generated:** La era moderna de la inteligencia artificial está dominada por el aprendizaje profundo, con su triunvirato de redes neuronales profundas, grandes datos y computadoras ultrafastas. Sin embargo, en la b...

**Confidence:** 0.05

---

### Issue 193 ✅ FIXED

**English:** FIGURE 48: Four straightforward instances of “walking a dog”

**Original Spanish:** (empty)

**🆕 LLM Generated:** Figura 48: Cuatro ejemplos directos de "pasear un perro" ±

**Confidence:** 0.05

---

### Issue 194 ✅ FIXED

**English:** While thinking about this topic, I was particularly taken by a delightful and insightful blog post written by Andrej Karpathy, the deep-learning and computer-vision expert who now directs AI efforts a...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Mientras reflexionaba sobre este tema, me cautivó particularmente un post de blog delicioso e iluminador escrito por Andrej Karpathy, experto en aprendizaje profundo y visión por computadora que ahora...

**Confidence:** 0.05

---

### Issue 195 ✅ FIXED

**English:** FIGURE 49: Four atypical instances of “walking a dog”

**Original Spanish:** (empty)

**🆕 LLM Generated:** Figura 49: Cuatro casos atípicos de "pasear a un perro" ±

**Confidence:** 0.05

---

### Issue 196 ✅ FIXED

**English:** Karpathy lists many of the things we humans easily understand but that remain beyond the abilities of today’s best computer-vision programs. For example, we recognize that there are people in the scen...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Karpathy enumera muchas cosas que entendemos fácilmente como seres humanos pero que siguen estando más allá de las capacidades de los mejores programas actuales de visión por ordenador. Por ejemplo, r...

**Confidence:** 0.05

---

### Issue 197 ✅ FIXED

**English:** Furthermore, we recognize that a person is standing on a scale, even though the scale is made up of white pixels that blend in with the background. Karpathy points out that we recognize that “Obama ha...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Además, reconocemos que hay una persona parada en una balanza, a pesar de que la balanza está compuesta por píxeles blancos que se confunden con el fondo. Karpathy señala que reconocemos que "Obama ti...

**Confidence:** 0.05

---

### Issue 198 ✅ FIXED

**English:** FIGURE 50: The photo discussed in Andrej Karpathy’s blog

**Original Spanish:** (empty)

**🆕 LLM Generated:** Figura 50: La foto discutida en el blog de Andrej Karpathy ±

**Confidence:** 0.05

---

### Issue 199 ✅ FIXED

**English:** Finally, we recognize that Obama and the other people observing this scene are smiling—we infer from their expressions that they are amused by the trick Obama is playing on the man on the scale, possi...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Finalmente, nos percatamos de que Obama y los demás observadores de esta escena están sonriendo; inferimos de sus expresiones que se divierten con la broma que Obama le está gastando al hombre de la b...

**Confidence:** 0.05

---

### Issue 200 ✅ FIXED

**English:** In summary, “It is mind-boggling that all of the above inferences unfold from a brief glance at a 2D array of [pixel] values.”

**Original Spanish:** (empty)

**🆕 LLM Generated:** En resumen, "Es asombroso que todas las inferencias anteriores surgen de una breve mirada a un arreglo bidimensional de valores [de píxel]." ±

**Confidence:** 0.05

---

### Issue 201 ✅ FIXED

**English:** For me, Karpathy’s example beautifully captures the complexity of human understanding and renders with crystal clarity the magnitude of the challenge for AI. Karpathy’s post was written in 2012, but i...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Para mí, el ejemplo de Karpathy captura con belleza la complejidad del entendimiento humano y muestra con claridad cristalina la magnitud del desafío para la IA. El post de Karpathy fue escrito en 201...

**Confidence:** 0.05

---

### Issue 202 ✅ FIXED

**English:** Karpathy concludes his post with this thought:

**Original Spanish:** (empty)

**🆕 LLM Generated:** Karpathy cierra su entrada con esta reflexión: ±

**Confidence:** 0.05

---

### Issue 203 ✅ FIXED

**English:** A seemingly inescapable conclusion for me is that we may … need embodiment, and that the only way to build computers that can interpret scenes like we do is to allow them to get exposed to all the yea...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Una conclusión que aparenta ser inevitable para mí es que possibly necesitemos la encarnación, y que el único modo de construir ordenadores capaces de interpretar escenas como lo hacemos nosotros es p...

**Confidence:** 0.05

---

### Issue 204 ✅ FIXED

**English:** In the seventeenth century, the philosopher René Descartes speculated that our bodies and our thoughts are made up of different substances and are subject to different physical laws.25 Since the 1950s...

**Original Spanish:** (empty)

**🆕 LLM Generated:** En el siglo diecisiete, el filósofo René Descartes especuló que nuestros cuerpos y nuestros pensamientos están compuestos de sustancias diferentes y están sujetos a leyes físicas distintas. Desde la d...

**Confidence:** 0.05

---

### Issue 205 🔁 DUPLICATE (FIXED)

**English:** 2.  In the following sections, quotations from Douglas Hofstadter are from a follow-up interview I did with him after the Google meeting; the quotations accurately capture the content and tone of his ...

**Original Spanish:** Agradecimientos Este libro debe su existencia a Douglas Hofstadter. Las obras de Doug fueron las que me atrajeron inicialmente a la IA, y sus ideas y su dirección guiaron mis estudios de doctorado. Má...

**🔁 Duplicate Fix:** En las secciones siguientes, las citas de Douglas Hofstadter son de una entrevista posterior que realicé con él después de la reunión de Google; las citas reflejan con precisión el contenido y el tono...

**Confidence:** 0.4062466621398926

---

### Issue 206 📏 OVER-LONG (FIXED)

**English:** 3.  Jack Schwartz, quoted in G.-C. Rota, Indiscrete Thoughts (Boston: Berkhäuser, 1997), 22.

**Original Spanish:** También quiero expresar mi gratitud a otros amigos y familiares que generosamente leyeron y comentar...

**📏 LLM Resized:** 3. Jack Schwartz, citado en G.-C. Rota, Pensamientos indiscretos (Boston: Berkhäuser, 1997), 22. ±

**Confidence:** 0.15

---

### Issue 207 📏 OVER-LONG (FIXED)

**English:** 4.  D. R. Hofstadter, Gödel, Escher, Bach: an Eternal Golden Braid (New York: Basic Books, 1979), 678.

**Original Spanish:** Muchas gracias a Eric Chinski, de Farrar, Straus and Giroux, por su estímulo y sus aportaciones siem...

**📏 LLM Resized:** 4. D.R. Hofstadter, Gödel, Escher, Bach: una trenza dorada eterna (Nueva York: Basic Books, 1979), 678. ±

**Confidence:** 0.15

---

### Issue 208 ✅ FIXED

**English:** 6.  Quoted in D. R. Hofstadter, “Staring Emmy Straight in the Eye—and Doing My Best Not to Flinch,” in Creativity, Cognition, and Knowledge, ed. T. Dartnell (Westport, Conn.: Praeger, 2002), 67–100.

**Original Spanish:** Estoy en deuda con mi marido, Kendall Springer, por su amor constante y su apoyo entusiasta, además de su paciencia y tolerancia para con mis enloquecidos hábitos de trabajo. Mis hijos, Jacob y Nichol...

**🔍 Vector Search (0.43):** Estoy en deuda con mi marido, Kendall Springer, por su amor constante y su apoyo entusiasta, además de su paciencia y tolerancia para con mis enloquecidos hábitos de trabajo. Mis hijos, Jacob y Nichol...

**✨ LLM Repair:** "Citado en D. R. Hofstadter, 'Mirando a Emmy directamente a los ojos... y tratando de no parpadear', en Creatividad, cognición y conocimiento, ed. T. Dartnell (Westport, Conn.: Praeger, 2002), pp. 67-...

**Confidence:** 0.436690092086792

---

### Issue 209 ✅ FIXED

**English:** 8.  M. McFarland, “Elon Musk: ‘With Artificial Intelligence, We Are Summoning the Demon,’” Washington Post, Oct. 24, 2014.

**Original Spanish:** (empty)

**🆕 LLM Generated:** 8. M. McFarland, "Elon Musk: 'Con la Inteligencia Artificial, Estamos Evocando al Demonio'", The Washington Post, 24 de octubre de 2014. ±

**Confidence:** 0.05

---

### Issue 210 ✅ FIXED

**English:** 9.  Bill Gates, on Reddit, Jan. 28, 2015, www.reddit.com/r/IAmA/comments/2tzjp7/hi_reddit_im_bill_gates_and_im_back_for_my_third/?.

**Original Spanish:** (empty)

**🆕 LLM Generated:** El 28 de enero de 2015, en Reddit. ±

**Confidence:** 0.05

---

### Issue 211 ✅ FIXED

**English:** 10.  Quoted in K. Anderson, “Enthusiasts and Skeptics Debate Artificial Intelligence,” Vanity Fair, Nov. 26, 2014.

**Original Spanish:** (empty)

**🆕 LLM Generated:** "No se ha encontrado ninguna fuente española para esta cita en inglés." ±

**Confidence:** 0.05

---

### Issue 212 ✅ FIXED

**English:** 11.  R. A. Brooks, “Mistaking Performance for Competence,” in What to Think About Machines That Think, ed. J. Brockman (New York: Harper Perennial, 2015), 108–11.

**Original Spanish:** (empty)

**🆕 LLM Generated:** 11. R.A. Brooks, "Confundiendo el Rendimiento con la Competencia", en ¿Qué Pensar sobre las Máquinas que Piensan?, ed. J. Brockman (Nueva York: Harper Perennial, 2015), 108-11. ±

**Confidence:** 0.05

---

### Issue 213 ✅ FIXED

**English:** 12.  Quoted in G. Press, “12 Observations About Artificial Intelligence from the O’Reilly AI Conference,” Forbes, Oct. 31, 2016, www.forbes.com/sites/gilpress/2016/10/31/12-observations-about-artifici...

**Original Spanish:** (empty)

**🆕 LLM Generated:** 12. Citado en G. Press, "12 observaciones sobre inteligencia artificial del congreso de O'Reilly AI", Forbes, 31 de octubre de 2016, www.forbes.com/sites/gilpress/2016/10/31/12-observations-about-arti...

**Confidence:** 0.05

---

### Issue 214 ✅ FIXED

**English:** 1: The Roots of Artificial Intelligence

**Original Spanish:** 03. La primavera de la IA

**🔍 Vector Search (0.41):** 03. La primavera de la IA

**✨ LLM Repair:** 1: Las Raíces de la Inteligencia Artificial ±

**Confidence:** 0.4056389629840851

---

### Issue 215 ✅ FIXED

**English:** 1.  J. McCarthy et al., “A Proposal for the Dartmouth Summer Research Project in Artificial Intelligence,” submitted to the Rockefeller Foundation, 1955, reprinted in AI Magazine 27, no. 4 (2006): 12–...

**Original Spanish:** (empty)

**🆕 LLM Generated:** 1. J. McCarthy et al., "Una propuesta para el proyecto de investigación de verano en inteligencia artificial de Dartmouth," presentado a la Fundación Rockefeller, 1955, reimpreso en AI Magazine 27, no...

**Confidence:** 0.05

---

### Issue 216 ✅ FIXED

**English:** 2.  Cybernetics was an interdisciplinary field that studied “control and communication in the animal and in machines.” See N. Wiener, Cybernetics (Cambridge, Mass.: MIT Press, 1961).

**Original Spanish:** Parte II. Mirar y ver

**🔍 Vector Search (0.44):** Parte II. Mirar y ver

**✨ LLM Repair:** "La cibernética era un campo interdisciplinario que estudiaba el 'control y comunicación en los animales y en las máquinas'. Ver N. Wiener, Cibernética (Cambridge, Mass.: MIT Press, 1961)."

The tone ...

**Confidence:** 0.44037479162216187

---

### Issue 217 ✅ FIXED

**English:** 3.  Quoted in N. J. Nilsson, John McCarthy: A Biographical Memoir (Washington, D.C.: National Academy of Sciences, 2012).

**Original Spanish:** (empty)

**🆕 LLM Generated:** "No se ha encontrado una traducción adecuada en español para mantener el tono y estilo de un libro literario sin añadir notas adicionales." ±

**Confidence:** 0.05

---

### Issue 218 ✅ FIXED

**English:** 4.  McCarthy et al., “Proposal for the Dartmouth Summer Research Project in Artificial Intelligence.”

**Original Spanish:** (empty)

**🆕 LLM Generated:** "4. McCarthy et al., “Propuesta para el Proyecto de Investigación de Verano en Inteligencia Artificial de Dartmouth”." ±

**Confidence:** 0.05

---

### Issue 219 ✅ FIXED

**English:** 6.  G. Solomonoff, “Ray Solomonoff and the Dartmouth Summer Research Project in Artificial Intelligence, 1956,” accessed Dec. 4, 2018, www.raysolomonoff.com/dartmouth/dartray.pdf.

**Original Spanish:** (empty)

**🆕 LLM Generated:** No se encontró una traducción literal mantenida en el tono y estilo de un libro literario para la entrada proporcionada. ±

**Confidence:** 0.05

---

### Issue 220 ✅ FIXED

**English:** 7.  H. Moravic, Mind Children: The Future of Robot and Human Intelligence (Cambridge, Mass.: Harvard University Press, 1988), 20.

**Original Spanish:** (empty)

**🆕 LLM Generated:** 7. H. Moravic, Niños de la mente: El futuro de la inteligencia robótica y humana (Cambridge, Mass.: Prensa de la Universidad de Harvard, 1988), 20. ±

**Confidence:** 0.05

---

### Issue 221 ✅ FIXED

**English:** 8.  H. A. Simon, The Shape of Automation for Men and Management (New York: Harper & Row, 1965), 96. Note that Simon’s use of man rather than person was par for the course in 1960s America.

**Original Spanish:** (empty)

**🆕 LLM Generated:** 8. H.A. Simon, La forma de la automatización para hombres y gestión (Nueva York: Harper & Row, 1965), 96. Notable que el uso que hace Simon de "man" en lugar de "person" era común en América en los añ...

**Confidence:** 0.05

---

### Issue 222 ✅ FIXED

**English:** 9.  M. L. Minsky, Computation: Finite and Infinite Machines (Upper Saddle River, N.J.: Prentice-Hall, 1967), 2.

**Original Spanish:** (empty)

**🆕 LLM Generated:** 9. M. L. Minsky, "Computación: Máquinas Finitas e Ilimitadas" (Upper Saddle River, N.J.: Prentice-Hall, 1967), 2. ±

**Confidence:** 0.05

---

### Issue 223 ✅ FIXED

**English:** 10.  B. R. Redman, The Portable Voltaire (New York: Penguin Books, 1977), 225.

**Original Spanish:** (empty)

**🆕 LLM Generated:** "10. B. R. Redman, Voltaire portátil (Nueva York: Penguin Books, 1977), 225." ±

**Confidence:** 0.05

---

### Issue 224 ✅ FIXED

**English:** 11.  M. L. Minsky, The Emotion Machine: Commonsense Thinking, Artificial Intelligence, and the Future of the Human Mind (New York: Simon & Schuster, 2006), 95.

**Original Spanish:** (empty)

**🆕 LLM Generated:** 11. M. L. Minsky, La máquina de las emociones: Pensamiento común, inteligencia artificial y el futuro de la mente humana (Nueva York: Simon & Schuster, 2006), 95. ±

**Confidence:** 0.05

---

### Issue 225 ✅ FIXED

**English:** 12.  One Hundred Year Study on Artificial Intelligence (AI100), 2016 Report, 13, ai100.stanford.edu/2016-report.

**Original Spanish:** (empty)

**🆕 LLM Generated:** Dieciséis años después del inicio de nuestro estudio centenario sobre Inteligencia Artificial, presentamos nuestro informe anual número trece. Puede encontrarlo en línea en nuestra página web, situada...

**Confidence:** 0.05

---

### Issue 226 ✅ FIXED

**English:** 14.  J. Lehman, J. Clune, and S. Risi, “An Anarchy of Methods: Current Trends in How Intelligence Is Abstracted in AI,” IEEE Intelligent Systems 29, no. 6 (2014): 56–62.

**Original Spanish:** (empty)

**🆕 LLM Generated:** "14. J. Lehman, J. Clune, y S. Risi, “Una Anarquía de Métodos: Tendencias Actuales en Cómo Se Abstrae la Inteligencia en IA”, IEEE Intelligent Systems 29, no. 6 (2014): 56-62." ±

**Confidence:** 0.05

---

### Issue 227 ✅ FIXED

**English:** 15.  A. Newell and H. A. Simon, “GPS: A Program That Simulates Human Thought,” P-2257, Rand Corporation, Santa Monica, Calif. (1961).

**Original Spanish:** (empty)

**🆕 LLM Generated:** "15. Newell y H.A. Simon, 'GPS: Un programa que simula el pensamiento humano', P-2257, Corporación RAND, Santa Mónica, California (1961)." ±

**Confidence:** 0.05

---

### Issue 228 ✅ FIXED

**English:** 16.  F. Rosenblatt, “The Perceptron: A Probabilistic Model for Information Storage and Organization in the Brain,” Psychological Review 65, no. 6 (1958): 386–408.

**Original Spanish:** (empty)

**🆕 LLM Generated:** 16. F. Rosenblatt, "El perceptrón: un modelo probabilístico para el almacenamiento y la organización de información en el cerebro", Revista de Psicología 65, nº 6 (1958): 386-408. ±

**Confidence:** 0.05

---

### Issue 229 ✅ FIXED

**English:** 17.  Mathematically, the perceptron-learning algorithm is the following. For each weight wj: wj ← wj + η (t − y) xj, where t is the correct output (1 or 0) for the given input, y is the actual output ...

**Original Spanish:** (empty)

**🆕 LLM Generated:** 17. En términos matemáticos, el algoritmo de aprendizaje del perceptrón es el siguiente. Para cada peso wj: wj ← wj + η (t − y) xj, donde t es la salida correcta (1 o 0) para la entrada dada, y es la ...

**Confidence:** 0.05

---

### Issue 230 ✅ FIXED

**English:** 18.  Quoted in M. Olazaran, “A Sociological Study of the Official History of the Perceptrons Controversy,” Social Studies of Science 26, no. 3 (1996): 611–59.

**Original Spanish:** (empty)

**🆕 LLM Generated:** "Citado en M. Olazaran, «Estudio sociológico de la historia oficial del conflicto de los perceptrones», Estudios sociales de la ciencia 26, núm. 3 (1996): 611-59." ±

**Confidence:** 0.05

---

### Issue 231 ✅ FIXED

**English:** 19.  M. A. Boden, Mind as Machine: A History of Cognitive Science (Oxford: Oxford University Press, 2006), 2:913.

**Original Spanish:** (empty)

**🆕 LLM Generated:** "19. M. A. Boden, 'La mente como máquina': Historia de la ciencia cognitiva (Oxford: Universidad de Oxford Press, 2006), 2:913." ±

**Confidence:** 0.05

---

### Issue 232 ✅ FIXED

**English:** 20.  M. L. Minsky and S. L. Papert, Perceptrons: An Introduction to Computational Geometry (Cambridge, Mass.: MIT Press, 1969).

**Original Spanish:** (empty)

**🆕 LLM Generated:** 20. M. L. Minsky y S. L. Papert, Perceptrones: Introducción a la geometría computacional (Cambridge, MA: Editorial MIT, 1969). ±

**Confidence:** 0.05

---

### Issue 233 ✅ FIXED

**English:** 21.  In technical terms, any Boolean function can be computed by a fully connected multilayer network with linear threshold units and one internal (“hidden”) layer.

**Original Spanish:** (empty)

**🆕 LLM Generated:** En términos técnicos, cualquier función booleana puede ser computada por una red multicapa completamente conectada con unidades de umbral lineal y una capa interna ("oculta"). ±

**Confidence:** 0.05

---

### Issue 234 ✅ FIXED

**English:** 22.  Olazaran, “Sociological Study of the Official History of the Perceptrons Controversy.”

**Original Spanish:** (empty)

**🆕 LLM Generated:** "22. Olazaran, 'Estudio Sociológico de la Historia Oficial de la Controvocracia de los Perceptrones'." ±

**Confidence:** 0.05

---

### Issue 235 ✅ FIXED

**English:** 23.  G. Nagy, “Neural Networks—Then and Now,” IEEE Transactions on Neural Networks 2, no. 2 (1991): 316–18.

**Original Spanish:** (empty)

**🆕 LLM Generated:** 23. G. Nagy, "Redes Neuronales—Ayer y Hoy", IEEE Transactions on Neural Networks, vol. 2, núm. 2 (1991): 316-18. ±

**Confidence:** 0.05

---

### Issue 236 ✅ FIXED

**English:** 24.  Minsky and Papert, Perceptrons, 231–32.

**Original Spanish:** (empty)

**🆕 LLM Generated:** 24. Minsky y Papert, Perceptrones, 231-32. ±

**Confidence:** 0.05

---

### Issue 237 ✅ FIXED

**English:** 25.  J. Lighthill, “Artificial Intelligence: A General Survey,” in Artificial Intelligence: A Paper Symposium (London: Science Research Council, 1973).

**Original Spanish:** (empty)

**🆕 LLM Generated:** 25. J. Lighthill, "Inteligencia Artificial: Una Revisión General", en Inteligencia Artificial: Un Simposio de Papers (Londres: Consejero Superior de Investigaciones Científicas, 1973). ±

**Confidence:** 0.05

---

### Issue 238 ✅ FIXED

**English:** 26.  Quoted in C. Moewes and A. Nürnberger, Computational Intelligence in Intelligent Data Analysis (New York: Springer, 2013), 135.

**Original Spanish:** 04. Quién, qué, cuándo, dónde, por qué

**🔍 Vector Search (0.24):** 04. Quién, qué, cuándo, dónde, por qué

**✨ LLM Repair:** En la página 135 de "Inteligencia Computacional en Análisis de Datos Inteligentes" de C. Moewes y A. Nürnberger (Nueva York: Springer, 2013). ±

**Confidence:** 0.21584127843379974

---

### Issue 239 ✅ FIXED

**English:** 27.  M. L. Minsky, The Society of Mind (New York: Simon & Schuster, 1987), 29.

**Original Spanish:** 05. ConvNet e ImageNet

**🔍 Vector Search (0.34):** 05. ConvNet e ImageNet

**✨ LLM Repair:** 27. M.L. Minsky, La sociedad de la mente (Nueva York: Simon & Schuster, 1987), 29. ±

**Confidence:** 0.20568035542964935

---

### Issue 240 📏 OVER-LONG (FIXED)

**English:** 2: Neural Networks and the Ascent of Machine Learning

**Original Spanish:** Pensemos en la estructura de nuestro cerebro, en el que algunas neuronas controlan directamente «sal...

**📏 LLM Resized:** CAPÍTULO II: Redes neuronales y la ascensión del aprendizaje automático ±

**Confidence:** 0.15

---

### Issue 241 ✅ FIXED

**English:** 3.  In my network with 324 inputs, 50 hidden units, and 10 output units, there are 324 × 50 = 16,200 weights from the inputs to the hidden layer, and 50 × 10 = 500 weights from the hidden layer to the...

**Original Spanish:** Para procesar una imagen como el ocho manuscrito de la figura 4, la red lleva a cabo sus cálculos capa a capa, de izquierda a derecha. Cada unidad oculta calcula su valor de activación; esos valores d...

**🔍 Vector Search (0.53):** Para procesar una imagen como el ocho manuscrito de la figura 4, la red lleva a cabo sus cálculos capa a capa, de izquierda a derecha. Cada unidad oculta calcula su valor de activación; esos valores d...

**✨ LLM Repair:** En mi red con 324 entradas, 50 unidades ocultas y 10 unidades de salida, existen 324 × 50 = 16,200 pesos desde las entradas hasta la capa oculta, y 50 × 10 = 500 pesos desde la capa oculta hasta la ca...

**Confidence:** 0.41820812225341797

---

### Issue 242 ✅ FIXED

**English:** 4.  D. E. Rumelhart, J. L. McClelland, and the PDP Research Group, Parallel Distributed Processing: Explorations in the Microstructure of Cognition (Cambridge, Mass.: MIT Press, 1986), 1:3.

**Original Spanish:** En teoría, una red neuronal multicapa puede aprender a utilizar sus unidades ocultas para reconocer características más abstractas (por ejemplo, formas como los «círculos» superior e inferior de un oc...

**🔍 Vector Search (0.53):** En teoría, una red neuronal multicapa puede aprender a utilizar sus unidades ocultas para reconocer características más abstractas (por ejemplo, formas como los «círculos» superior e inferior de un oc...

**✨ LLM Repair:** 4. D. E. Rumelhart, J. L. McClelland y el Grupo de Investigación PDP, Procesamiento Distribuido en Paralelo: Exploraciones en la Microestructura de la Cognición (Cambridge, Mass.: MIT Press, 1986), Vo...

**Confidence:** 0.39788711071014404

---

### Issue 243 ✅ FIXED

**English:** 6.  Quoted in C. Johnson, “Neural Network Startups Proliferate Across the U.S.,” The Scientist, Oct. 17, 1988.

**Original Spanish:** En su libro Perceptrons, Minsky y Papert se mostraban escépticos ante la posibilidad de diseñar un algoritmo capaz de aprender los pesos de una red neuronal multicapa.

**🔍 Vector Search (0.40):** En su libro Perceptrons, Minsky y Papert se mostraban escépticos ante la posibilidad de diseñar un algoritmo capaz de aprender los pesos de una red neuronal multicapa.

**✨ LLM Repair:** 6. Citado en C. Johnson, "Startups de redes neuronales proliferan en todo Estados Unidos", El Científico, 17 de octubre de 1988. ±

**Confidence:** 0.37832537293434143

---

### Issue 244 ✅ FIXED

**English:** 7.  A. Clark, Being There: Putting Brain, Body, and World Together Again (Cambridge, Mass.: MIT Press, 1996), 26.

**Original Spanish:** Su escepticismo, unido a las dudas de otros estudiosos de la IA simbólica, fue una de las principales razones de que disminuyeran bruscamente los fondos para la investigación sobre redes neuronales en...

**🔍 Vector Search (0.36):** Su escepticismo, unido a las dudas de otros estudiosos de la IA simbólica, fue una de las principales razones de que disminuyeran bruscamente los fondos para la investigación sobre redes neuronales en...

**✨ LLM Repair:** "7. A. Clark, Estar Aquí: Volviendo a unir cerebro, cuerpo y mundo de nuevo (Cambridge, Mass.: Editorial MIT Press, 1996), página 26." ±

**Confidence:** 0.24313323199748993

---

### Issue 245 ✅ FIXED

**English:** 8.  As Douglas Hofstadter pointed out to me, the grammatically correct version is “good old old-fashioned AI,” but GOOFAI doesn’t have the same ring as GOFAI.

**Original Spanish:** Sin embargo, a pesar del jarro de agua fría que supuso el libro de Minsky y Papert, un pequeño grupo de investigadores sobre redes neuronales persistió, sobre todo en el campo de la psicología cogniti...

**🔍 Vector Search (0.34):** Sin embargo, a pesar del jarro de agua fría que supuso el libro de Minsky y Papert, un pequeño grupo de investigadores sobre redes neuronales persistió, sobre todo en el campo de la psicología cogniti...

**✨ LLM Repair:** Como Douglas Hofstadter me señaló, la versión gramaticalmente correcta es "el buen antiguo estilo anticuado de la inteligencia artificial", pero eso no tiene el mismo sonido que GOFAI. ±

**Confidence:** 0.3259202539920807

---

### Issue 246 📏 OVER-LONG (FIXED)

**English:** 4: Who, What, When, Where, Why

**Original Spanish:** Como su nombre indica, la retropropagación consiste en fijarse en un error observado en las unidades...

**📏 LLM Resized:** Cuatro: Quién, Qué, Cuándo, Dónde, Por qué ±

**Confidence:** 0.15

---

### Issue 247 ✅ FIXED

**English:** 1.  S. A. Papert, “The Summer Vision Project,” MIT Artificial Intelligence Group Vision Memo 100 (July 7, 1966), dspace.mit.edu/handle/1721.1/6125.

**Original Spanish:** La retropropagación funciona (al menos en teoría) independientemente del número de entradas, unidades ocultas o unidades de salida que tenga la red neuronal.

**🔍 Vector Search (0.45):** La retropropagación funciona (al menos en teoría) independientemente del número de entradas, unidades ocultas o unidades de salida que tenga la red neuronal.

**✨ LLM Repair:** 1. S.A. Papert, "El proyecto de visión de verano", Memorando del grupo de visión MIT Artificial Intelligence Group Nº 100 (7 de julio de 1966), dspace.mit.edu/handle/1721.1/6125. ±

**Confidence:** 0.3125254511833191

---

### Issue 248 ✅ FIXED

**English:** 2.  D. Crevier, AI: The Tumultuous History of the Search for Artificial Intelligence (New York: Basic Books, 1993), 88.

**Original Spanish:** Aunque no existen garantías matemáticas de que la retropropagación resuelva los pesos correctos para una red, en la práctica ha conseguido buenos resultados en muchas tareas que son demasiado difícile...

**🔍 Vector Search (0.48):** Aunque no existen garantías matemáticas de que la retropropagación resuelva los pesos correctos para una red, en la práctica ha conseguido buenos resultados en muchas tareas que son demasiado difícile...

**✨ LLM Repair:** 2. D. Crevier, IA: La historia tumultuosa de la búsqueda de inteligencia artificial (Nueva York: Basic Books, 1993), 88. ±

**Confidence:** 0.33727335929870605

---

### Issue 249 ✅ FIXED

**English:** 5.  Most claims about how the brain performs some task have to come with many caveats; the story I’ve just outlined is no different. While what I’ve said is approximately accurate, the brain is outrag...

**Original Spanish:** Las redes neuronales se han utilizado en ámbitos tan distintos como el reconocimiento de voz, las predicciones en el mercado bursátil, la traducción y la composición musical.

**🔍 Vector Search (0.54):** Las redes neuronales se han utilizado en ámbitos tan distintos como el reconocimiento de voz, las predicciones en el mercado bursátil, la traducción y la composición musical.

**✨ LLM Repair:** 5. La mayoría de las afirmaciones sobre cómo el cerebro realiza alguna tarea vienen con muchas reservas; la historia que acabo de contar no es diferente. Aunque lo que he dicho es aproximadamente prec...

**Confidence:** 0.2549040913581848

---

### Issue 250 ✅ FIXED

**English:** 6.  The array of weights associated with each activation map is called a convolutional filter or convolutional kernel.

**Original Spanish:** Conexionismo

**🔍 Vector Search (0.25):** Conexionismo

**✨ LLM Repair:** "El conjunto de pesos asociado con cada mapa de activación se llama filtro convolucional o núcleo convolucional." ±

**Confidence:** 0.08120200037956238

---

### Issue 251 📏 OVER-LONG (FIXED)

**English:** 7.  Here I’m using the term classification module as shorthand for what are usually called the fully connected layers of a deep convolutional network.

**Original Spanish:** En los años ochenta, el grupo más conocido del campo de las redes neuronales era un equipo de la Uni...

**📏 LLM Resized:** 7. Aquí empleo el término módulo de clasificación como una forma abreviada de lo que normalmente se llama las capas completamente conectadas de una red convolucional profunda. ±

**Confidence:** 0.15

---

### Issue 252 ✅ FIXED

**English:** 8.  My description of ConvNets leaves out many details. For example, to compute its activation, a unit in a convolutional layer performs a convolution and then applies a nonlinear activation function ...

**Original Spanish:** De hecho, a mediados de los años ochenta, los sistemas expertos —unos enfoques de IA simbólica que se basan en los humanos para crear reglas que reflejen el conocimiento experto de un ámbito concreto—...

**🔍 Vector Search (0.52):** De hecho, a mediados de los años ochenta, los sistemas expertos —unos enfoques de IA simbólica que se basan en los humanos para crear reglas que reflejen el conocimiento experto de un ámbito concreto—...

**✨ LLM Repair:** 8. Mi descripción de ConvNets omite muchos detalles. Por ejemplo, para calcular su activación, una unidad en una capa convolucional realiza una convolución y luego aplica una función de activación no ...

**Confidence:** 0.4059537649154663

---

### Issue 253 📏 OVER-LONG (FIXED)

**English:** 9.  At the time of this writing, Google’s “search by image” engine is accessed at images.google.com by clicking the small camera icon in the search box.

**Original Spanish:** Los partidarios del conexionismo decían que las claves de la inteligencia eran una arquitectura comp...

**📏 LLM Resized:** Al momento de escribir esto, se accede al motor de búsqueda de imágenes de Google en images.google.com haciendo clic en el pequeño icono de cámara en el cuadro de búsqueda. ±

**Confidence:** 0.15

---

### Issue 254 ✅ FIXED

**English:** 1.  Indeed, back-propagation is an algorithm that was discovered independently by several different groups, and—ironically, given back-propagation’s function as a credit-assignment algorithm—assigning...

**Original Spanish:** Durante las seis décadas de investigación sobre IA ha habido repetidos debates sobre las ventajas y los inconvenientes relativos de los enfoques simbólico y subsimbólico. Los sistemas simbólicos puede...

**🔍 Vector Search (0.56):** Durante las seis décadas de investigación sobre IA ha habido repetidos debates sobre las ventajas y los inconvenientes relativos de los enfoques simbólico y subsimbólico. Los sistemas simbólicos puede...

**✨ LLM Repair:** En efecto, la retropropagación es un algoritmo que fue descubierto de forma independiente por varios grupos diferentes, y, irónicamente, dado el papel de la retropropagación como algoritmo de asignaci...

**Confidence:** 0.41054096817970276

---

### Issue 255 ✅ FIXED

**English:** 3.  There was also a “detection” competition, in which programs had to also locate objects of the various categories in images, as well as other specialized challenges; here I’m focusing on the classi...

**Original Spanish:** Entonces, ¿por qué no utilizar sistemas simbólicos para las tareas que requieren descripciones casi lingüísticas y razonamientos lógicos de alto nivel, y emplear sistemas subsimbólicos para las tareas...

**🔍 Vector Search (0.41):** Entonces, ¿por qué no utilizar sistemas simbólicos para las tareas que requieren descripciones casi lingüísticas y razonamientos lógicos de alto nivel, y emplear sistemas subsimbólicos para las tareas...

**✨ LLM Repair:** También había una competición de "detectación", en la que los programas debían encontrar objetos de diversas categorías en imágenes, así como otros desafíos especializados; me centro aquí en el desafí...

**Confidence:** 0.4365408420562744

---

### Issue 256 ✅ FIXED

**English:** 4.  D. Gershgorn, “The Data That Transformed AI Research—and Possibly the World,” Quartz, July 26, 2017, qz.com/1034972/the-data-that-changed-the-direction-of-ai-research-and-possibly-the-world/.

**Original Spanish:** Aunque ha habido algunos intentos de construir sistemas híbridos que incluyan métodos subsimbólicos y simbólicos, todavía no hay ninguno que haya tenido un éxito digno de mención.

**🔍 Vector Search (0.45):** Aunque ha habido algunos intentos de construir sistemas híbridos que incluyan métodos subsimbólicos y simbólicos, todavía no hay ninguno que haya tenido un éxito digno de mención.

**✨ LLM Repair:** "4. D. Gershgorn, “Los datos que transformaron la investigación de IA (y possibly al mundo)”, Quartz, 26 de julio de 2017, qz.com/1034972/los-datos-que-cambiaron-la-direccion-de-la-investigacion-de-ia...

**Confidence:** 0.2758810818195343

---

### Issue 257 ✅ FIXED

**English:** 6.  L. Fei-Fei and J. Deng, “ImageNet: Where Have We Been? Where Are We Going?,” slides at image-net.org/challenges/talks_2017/imagenet_ilsvrc2017_v1.0.pdf.

**Original Spanish:** Inspirándose en la estadística y la teoría de la probabilidad, los investigadores de la IA desarrollaron numerosos algoritmos que hacen que los ordenadores puedan aprender de los datos, y el campo del...

**🔍 Vector Search (0.37):** Inspirándose en la estadística y la teoría de la probabilidad, los investigadores de la IA desarrollaron numerosos algoritmos que hacen que los ordenadores puedan aprender de los datos, y el campo del...

**✨ LLM Repair:** 6. L. Fei-Fei y J. Deng, "ImageNet: ¿Dónde hemos estado? ¿Adónde vamos?", diapositivas en imagenet.org/challenges/talks_2017/imagenet_ilsvrc2017_v1.0.pdf. ±

**Confidence:** 0.36954599618911743

---

### Issue 258 ✅ FIXED

**English:** 7.  A. Krizhevsky, I. Sutskever, and G. E. Hinton, “ImageNet Classification with Deep Convolutional Neural Networks,” Advances in Neural Information Processing Systems 25 (2012): 1097–105.

**Original Spanish:** Los investigadores sobre aprendizaje automático hablaban de los métodos simbólicos de la IA en tono despectivo, llamándolos la IA pasada de moda, o GOFAI (siglas correspondientes a good old-fashioned ...

**🔍 Vector Search (0.39):** Los investigadores sobre aprendizaje automático hablaban de los métodos simbólicos de la IA en tono despectivo, llamándolos la IA pasada de moda, o GOFAI (siglas correspondientes a good old-fashioned ...

**✨ LLM Repair:** "7. A. Krizhevsky, I. Sutskever y G. E. Hinton, 'Clasificación de ImageNet con redes neuronales convolucionales profundas', Avances en Procesamiento de Información y Sistemas Neurales 25 (2012): 1097–...

**Confidence:** 0.3818359375

---

### Issue 259 ✅ FIXED

**English:** 8.  T. Simonite, “Teaching Machines to Understand Us,” Technology Review, Aug. 5, 2015, www.technologyreview.com/s/540001/teaching-machines-to-understand-us/.

**Original Spanish:** (empty)

**🆕 LLM Generated:** 8. T. Simonite, "Enseñando a las Máquinas a Comprendernos", Technology Review, 5 de agosto de 2015, www.technologyreview.com/s/540001/enseñando-a-las-máquinas-a-comprendernos/. ±

**Confidence:** 0.05

---

### Issue 260 ✅ FIXED

**English:** 9.  ImageNet Large Scale Visual Recognition Challenge announcement, June 2, 2015, www.image-net.org/challenges/LSVRC/announcement-June-2-2015.

**Original Spanish:** (empty)

**🆕 LLM Generated:** El anuncio del desafío de reconocimiento visual a gran escala ImageNet se publicó el 2 de junio de 2015 en www.image-net.org/challenges/LSVRC/anuncio-del-2-de-junio-de-2015. ±

**Confidence:** 0.05

---

### Issue 261 ✅ FIXED

**English:** 10.  S. Chen, “Baidu Fires Scientist Responsible for Breaching Rules in High-Profile Supercomputer AI Test,” South China Morning Post, international edition, June 12, 2015, www.scmp.com/tech/science-r...

**Original Spanish:** (empty)

**🆕 LLM Generated:** El 12 de junio de 2015, el South China Morning Post informó que Baidu había despedido a un científico responsable de violar las reglas en una prueba de superordenador de inteligencia artificial de alt...

**Confidence:** 0.05

---

### Issue 262 ✅ FIXED

**English:** 11.  Gershgorn, “Data That Transformed AI Research.”

**Original Spanish:** (empty)

**🆕 LLM Generated:** 11. Gershgorn, "Los datos que transformaron la investigación de IA". ±

**Confidence:** 0.05

---

### Issue 263 ✅ FIXED

**English:** 12.  Quoted in Hernandez, “Facebook’s Quest to Build an Artificial Brain Depends on This Guy.”

**Original Spanish:** (empty)

**🆕 LLM Generated:** "Citado en Hernandez, 'La búsqueda de Facebook para construir un cerebro artificial depende de este tipo.'" ±

**Confidence:** 0.05

---

### Issue 264 ✅ FIXED

**English:** 13.  B. Agüera y Arcas, “Inside the Machine Mind: Latest Insights on Neuroscience and Computer Science from Google” (lecture video), Oxford Martin School, May 10, 2016, www.youtube.com/watch?v=v1dW7Vi...

**Original Spanish:** (empty)

**🆕 LLM Generated:** "13. B. Agüera y Arcas, “Dentro de la mente de la máquina: últimas perspectivas sobre neurociencia y ciencias de la computación desde Google” (vídeo de conferencia), Oxford Martin School, 10 de mayo d...

**Confidence:** 0.05

---

### Issue 265 ✅ FIXED

**English:** 14.  K. He et al., “Delving Deep into Rectifiers: Surpassing Human-Level Performance on ImageNet Classification,” in Proceedings of the IEEE International Conference on Computer Vision (2015), 1026–34...

**Original Spanish:** (empty)

**🆕 LLM Generated:** 14. K. He et al., "Sumergiéndonos en los rectificadores: superando el rendimiento humano en la clasificación de ImageNet", en Actas de la conferencia internacional sobre visión por computadora del IEE...

**Confidence:** 0.05

---

### Issue 266 ✅ FIXED

**English:** 15.  A. Linn, “Microsoft Researchers Win ImageNet Computer Vision Challenge,” AI Blog, Microsoft, Dec. 10, 2015, blogs.microsoft.com/ai/2015/12/10/microsoft-researchers-win-imagenet-computer-vision-ch...

**Original Spanish:** (empty)

**🆕 LLM Generated:** 15. A. Linn, "Investigadores de Microsoft Ganaron el Desafío de Visión por Computadora ImageNet", Blog de IA, Microsoft, 10 de diciembre de 2015, blogs.microsoft.com/ai/2015/12/10/microsoft-researcher...

**Confidence:** 0.05

---

### Issue 267 ✅ FIXED

**English:** 16.  A. Hern, “Computers Now Better than Humans at Recognising and Sorting Images,” Guardian, May 13, 2015, www.theguardian.com/global/2015/may/13/baidu-minwa-supercomputer-better-than-humans-recognis...

**Original Spanish:** (empty)

**🆕 LLM Generated:** 16. A. Hern, “Los ordenadores ahora superan a los humanos en el reconocimiento y clasificación de imágenes”, The Guardian, 13 de mayo de 2015, www.theguardian.com/technology/2015/may/13/computers-now-...

**Confidence:** 0.05

---

### Issue 268 ✅ FIXED

**English:** 17.  A. Karpathy, “What I Learned from Competing Against a ConvNet on ImageNet,” Sept. 2, 2014, karpathy.github.io/2014/09/02/what-i-learned-from-competing-against-a-convnet-on-imagenet.

**Original Spanish:** (empty)

**🆕 LLM Generated:** 17. A. Karpathy, “Lo que aprendí compitiendo contra una ConvNet en ImageNet,” 2 de septiembre de 2014, karpathy.github.io/2014/09/02/what-i-learned-from-competing-against-a-convnet-on-imagenet. ±

**Confidence:** 0.05

---

### Issue 269 📏 OVER-LONG (FIXED)

**English:** 18.  S. Lohr, “A Lesson of Tesla Crashes? Computer Vision Can’t Do It All Yet,” New York Times, Sept. 19, 2016.

**Original Spanish:** Durante las dos décadas siguientes, el aprendizaje automático también tuvo sus ciclos de optimismo, ...

**📏 LLM Resized:** "18. S. Lohr, “Lección de los accidentes de Tesla: la visión por computadora aún no lo puede hacer todo”, The New York Times, septiembre de 2016." ±

**Confidence:** 0.15

---

### Issue 270 ✅ FIXED

**English:** 6: A Closer Look at Machines That Learn

**Original Spanish:** 09. A jugar

**🔍 Vector Search (0.40):** 09. A jugar

**✨ LLM Repair:** 6: Un examen más detallado de las máquinas que aprenden ±

**Confidence:** 0.34683483839035034

---

### Issue 271 ✅ FIXED

**English:** 1.  Readers who followed the 2016 U.S. presidential election will recognize the pun on Bernie Sanders’s supporters’ tagline, “Feel the Bern.”

**Original Spanish:** (empty)

**🆕 LLM Generated:** 1. Los lectores que siguieron la elección presidencial de EE.UU. en 2016 reconocerán el juego de palabras en el lema de los seguidores de Bernie Sanders, "Siente el ardor". ±

**Confidence:** 0.05

---

### Issue 272 ✅ FIXED

**English:** 2.  E. Brynjolfsson and A. McAfee, “The Business of Artificial Intelligence,” Harvard Business Review, July 2017.

**Original Spanish:** 10. Más allá de los juegos

**🔍 Vector Search (0.33):** 10. Más allá de los juegos

**✨ LLM Repair:** 2. E. Brynjolfsson y A. McAfee, "El Negocio de la Inteligencia Artificial", Harvard Business Review, julio de 2017. ±

**Confidence:** 0.2680538296699524

---

### Issue 273 ✅ FIXED

**English:** 3.  O. Tanz, “Can Artificial Intelligence Identify Pictures Better than Humans?,” Entrepreneur, April 1, 2017, www.entrepreneur.com/article/283990.

**Original Spanish:** (empty)

**🆕 LLM Generated:** "¿Puede la inteligencia artificial identificar imágenes mejor que los humanos?" O. Tanz, Entrepreneur, 1 de abril de 2017, www.entrepreneur.com/article/283990. ±

**Confidence:** 0.05

---

### Issue 274 ✅ FIXED

**English:** 4.  D. Vena, “3 Top AI Stocks to Buy Now,” Motley Fool, March 27, 2017, www.fool.com/investing/2017/03/27/3-top-ai-stocks-to-buy-now.aspx.

**Original Spanish:** (empty)

**🆕 LLM Generated:** 4. D. Vena, “3 Acciones de IA para Comprar Ahora”, Motley Fool, 27 de marzo de 2017, www.fool.com/investing/2017/03/27/3-top-ai-stocks-to-buy-now.aspx ±

**Confidence:** 0.05

---

### Issue 275 ✅ FIXED

**English:** 5.  Quoted in C. Metz, “A New Way for Machines to See, Taking Shape in Toronto,” New York Times, Nov. 28, 2017, www.nytimes.com/2017/11/28/technology/artificial-intelligence-research-toronto.html.

**Original Spanish:** (empty)

**🆕 LLM Generated:** "5. Citado en C. Metz, “Una nueva forma para que las máquinas vean, tomando forma en Toronto”, The New York Times, 28 de noviembre de 2017, www.nytimes.com/2017/11/28/technology/artificial-intelligenc...

**Confidence:** 0.05

---

### Issue 276 ✅ FIXED

**English:** 6.  Quoted in J. Tanz, “Soon We Won’t Program Computers. We’ll Train Them Like Dogs,” Wired, May 17, 2016.

**Original Spanish:** (empty)

**🆕 LLM Generated:** “Pronto no programaremos computadoras. Las entrenaremos como perros.” ±

**Confidence:** 0.05

---

### Issue 277 ✅ FIXED

**English:** 7.  From Harry Shum’s lecture at the Microsoft Faculty Summit, Redmond, Wash., June 2017.

**Original Spanish:** (empty)

**🆕 LLM Generated:** 7. De la charla de Harry Shum en la Cumbre de Profesores de Microsoft, Redmond, Wa., junio de 2017. ±

**Confidence:** 0.05

---

### Issue 278 ✅ FIXED

**English:** 8.  An in-depth discussion of this issue is given in J. Lanier, Who Owns the Future? (New York: Simon & Schuster, 2013).

**Original Spanish:** (empty)

**🆕 LLM Generated:** "Se proporciona una discusión exhaustiva sobre este tema en '¿Quién posee el futuro?' de J. Lanier (Nueva York: Simon & Schuster, 2013)." ±

**Confidence:** 0.05

---

### Issue 279 ✅ FIXED

**English:** 9.  Tesla’s Customer Privacy Policy, accessed Dec. 7, 2018, www.tesla.com/about/legal.

**Original Spanish:** (empty)

**🆕 LLM Generated:** Política de privacidad del cliente de Tesla, acceso el 7 de diciembre de 2018, www.tesla.com/acerca/de/legal. ±

**Confidence:** 0.05

---

### Issue 280 ✅ FIXED

**English:** 10.  T. Bradshaw, “Self-Driving Cars Prove to Be Labour-Intensive for Humans,” Financial Times, July 8, 2017.

**Original Spanish:** (empty)

**🆕 LLM Generated:** "10. T. Bradshaw, “Los coches autónomos resultan intensivos en trabajo para los humanos”, Financial Times, 8 de julio de 2017." ±

**Confidence:** 0.05

---

### Issue 281 ✅ FIXED

**English:** 11.  “Ground Truth Datasets for Autonomous Vehicles,” Mighty AI, accessed Dec. 7, 2018, mty.ai/adas/.

**Original Spanish:** Parte IV. La inteligencia artificial entra en contacto con el lenguaje natural

**🔍 Vector Search (0.40):** Parte IV. La inteligencia artificial entra en contacto con el lenguaje natural

**✨ LLM Repair:** "11. “Conjuntos de datos verdaderos para vehículos autónomos”, Mighty AI, consultado el 7 de diciembre de 2018, mty.ai/adas./" ±

**Confidence:** 0.36959025263786316

---

### Issue 282 ✅ FIXED

**English:** 12.  “Deep Learning in Practice: Speech Recognition and Beyond,” EmTech Digital video, May 23, 2016, events.technologyreview.com/emtech/digital/16/video/watch/andrew-ng-deep-learning.

**Original Spanish:** (empty)

**🆕 LLM Generated:** "12. “El aprendizaje profundo en la práctica: reconocimiento del habla y más allá”, EmTech Digital video, 23 de mayo de 2016, events.technologyreview.com/emtech/digital/16/video/watch/andrew-ng-deep-l...

**Confidence:** 0.05

---

### Issue 283 ✅ FIXED

**English:** 13.  Y. Bengio, “Machines That Dream,” in The Future of Machine Intelligence: Perspectives from Leading Practitioners, ed. D. Beyer (Sebastopol, Calif.: O’Reilly Media), 14.

**Original Spanish:** (empty)

**🆕 LLM Generated:** "13. Y. Bengio, "Máquinas que sueñan", en El futuro de la inteligencia artificial: perspectivas de los principales practicantes, editado por D. Beyer (Sebastopol, California: O'Reilly Media), 14." ±

**Confidence:** 0.05

---

### Issue 284 ✅ FIXED

**English:** 14.  W. Landecker et al., “Interpreting Individual Classifications of Hierarchical Networks,” in Proceedings of the 2013 IEEE Symposium on Computational Intelligence and Data Mining (2013), 32–38.

**Original Spanish:** (empty)

**🆕 LLM Generated:** "14. W. Landecker, et al., 'Interpretando clasificaciones individuales de redes jerárquicas', en Actas del simposio de inteligencia computacional y minería de datos de la IEEE 2013 (2013), pp. 32-38."...

**Confidence:** 0.05

---

### Issue 285 ✅ FIXED

**English:** 15.  M. R. Loghmani et al., “Recognizing Objects in-the-Wild: Where Do We Stand?,” in IEEE International Conference on Robotics and Automation (2018), 2170–77.

**Original Spanish:** (empty)

**🆕 LLM Generated:** En la XV edición de la Conferencia Internacional sobre Robótica y Automatización de la IEEE (2018), los autores M. R. Loghmani et al., presentaron un trabajo titulado "Reconocimiento de objetos en la ...

**Confidence:** 0.05

---

### Issue 286 ✅ FIXED

**English:** 16.  H. Hosseini et al., “On the Limitation of Convolutional Neural Networks in Recognizing Negative Images,” in Proceedings of the 16th IEEE International Conference on Machine Learning and Applicati...

**Original Spanish:** (empty)

**🆕 LLM Generated:** 16. H. Hosseini, et al., "Sobre la Limitación de las Redes Neuronales Convolucionales en el Reconocimiento de Imágenes Negativas", en "Proceedings of the 16th IEEE International Conference on Machine ...

**Confidence:** 0.05

---

### Issue 287 ✅ FIXED

**English:** 17.  M. Orcutt, “Are Face Recognition Systems Accurate? Depends on Your Race,” Technology Review, July 6, 2016, www.technologyreview.com/s/601786/are-face-recognition-systems-accurate-depends-on-your-...

**Original Spanish:** (empty)

**🆕 LLM Generated:** "17. M. Orcutt, “¿Son los sistemas de reconocimiento facial precisos? Depende de tu raza”, Technology Review, 6 de julio de 2016, www.technologyreview.com/s/601786/are-face-recognition-systems-accurat...

**Confidence:** 0.05

---

### Issue 288 ✅ FIXED

**English:** 18.  J. Zhao et al., “Men Also Like Shopping: Reducing Gender Bias Amplification Using Corpus-Level Constraints,” in Proceedings of the 2017 Conference on Empirical Methods in Natural Language Process...

**Original Spanish:** (empty)

**🆕 LLM Generated:** "18. J. Zhao et al., 'También a los hombres les gusta ir de compras: reducción de la amplificación de sesgos de género mediante restricciones a nivel de corpus', en Actas de la Conferencia sobre Métod...

**Confidence:** 0.05

---

### Issue 289 ✅ FIXED

**English:** 19.  W. Knight, “The Dark Secret at the Heart of AI,” Technology Review, April 11, 2017, www.technologyreview.com/s/604087/the-dark-secret-at-the-heart-of-ai/.

**Original Spanish:** (empty)

**🆕 LLM Generated:** 19. W. Knight, "El oscuro secreto en el corazón del IA", Tecnología Review, 11 de abril de 2017, www.technologyreview.com/s/604087/the-dark-secret-at-the-heart-of-ai/. ±

**Confidence:** 0.05

---

### Issue 290 ✅ FIXED

**English:** 20.  C. Szegedy et al., “Intriguing Properties of Neural Networks,” in Proceedings of the International Conference on Learning Representations (2014).

**Original Spanish:** (empty)

**🆕 LLM Generated:** "20. C. Szegedy et al., ‘Propiedades intrigantes de las redes neuronales’, en las Actas de la Conferencia Internacional sobre el Aprendizaje de Representaciones (2014)." ±

**Confidence:** 0.05

---

### Issue 291 ✅ FIXED

**English:** 21.  A. Nguyen, J. Yosinski, and J. Clune, “Deep Neural Networks Are Easily Fooled: High Confidence Predictions for Unrecognizable Images,” in Proceedings of the IEEE Conference on Computer Vision and...

**Original Spanish:** (empty)

**🆕 LLM Generated:** 21. A. Nguyen, J. Yosinski y J. Clune, "Las redes neuronales profundas son fácilmente engañadas: predicciones de alta confianza para imágenes irreconocibles", en "Actas de la Conferencia de la IEEE so...

**Confidence:** 0.05

---

### Issue 292 ✅ FIXED

**English:** 22.  See, for example, M. Mitchell, An Introduction to Genetic Algorithms (Cambridge, Mass.: MIT Press, 1996).

**Original Spanish:** (empty)

**🆕 LLM Generated:** Véase, por ejemplo, M. Mitchell, Introducción a los Algoritmos Genéticos (Cambridge, MA: Editorial MIT, 1996). ±

**Confidence:** 0.05

---

### Issue 293 ✅ FIXED

**English:** 23.  Nguyen, Yosinski, and Clune, “Deep Neural Networks Are Easily Fooled.”

**Original Spanish:** (empty)

**🆕 LLM Generated:** "23. Nguyen, Yosinski, y Clune, 'Las redes neuronales profundas son fácilmente engañadas.'" ±

**Confidence:** 0.05

---

### Issue 294 ✅ FIXED

**English:** 24.  M. Sharif et al., “Accessorize to a Crime: Real and Stealthy Attacks on State-of-the-Art Face Recognition,” in Proceedings of the 2016 ACM SIGSAC Conference on Computer and Communications Securit...

**Original Spanish:** (empty)

**🆕 LLM Generated:** 24. M. Sharif et al., "Acesorios hasta el Crimen: Ataques Reales y Sigilosos en el Reconocimiento Facial de Estado del Arte", en "Proceedings of the 2016 ACM SIGSAC Conference on Computer and Communic...

**Confidence:** 0.05

---

### Issue 295 ✅ FIXED

**English:** 25.  K. Eykholt et al., “Robust Physical-World Attacks on Deep Learning Visual Classification,” in Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition (2018), 1625–34.

**Original Spanish:** (empty)

**🆕 LLM Generated:** 25. K. Eykholt et al., "Ataques robustos en el mundo físico contra la clasificación visual de aprendizaje profundo", en Actas de la Conferencia de la IEEE sobre Visión Artificial y Reconocimiento de P...

**Confidence:** 0.05

---

### Issue 296 ✅ FIXED

**English:** 26.  S. G. Finlayson et al., “Adversarial Attacks on Medical Machine Learning,” Science 363, no. 6433 (2019): 1287–89.

**Original Spanish:** (empty)

**🆕 LLM Generated:** 26. S.G. Finlayson et al., "Ataques adversariales en aprendizaje automático médico", Ciencia 363, n.º 6433 (2019): 1287-89. ±

**Confidence:** 0.05

---

### Issue 297 ✅ FIXED

**English:** 27.  Quoted in W. Knight, “How Long Before AI Systems Are Hacked in Creative New Ways?,” Technology Review, Dec. 15, 2016, www.technologyreview.com/s/603116/how-long-before-ai-systems-are-hacked-in-cr...

**Original Spanish:** (empty)

**🆕 LLM Generated:** "No se sabe cuánto tiempo pasará antes de que los sistemas de IA sean pirateados de maneras creativas y nuevas." ±

**Confidence:** 0.05

---

### Issue 298 ✅ FIXED

**English:** 28.  J. Clune, “How Much Do Deep Neural Networks Understand About the Images They Recognize?,” lecture slides (2016), accessed Dec. 7, 2018, c4dm.eecs.qmul.ac.uk/horse2016/HORSE2016_Clune.pdf.

**Original Spanish:** (empty)

**🆕 LLM Generated:** No se han encontrado resultados para la traducción de este texto al español. Por favor, proporcione más contexto o información sobre el tono y estilo deseados para una traducción más precisa. ±

**Confidence:** 0.05

---

### Issue 299 ✅ FIXED

**English:** 7: On Trustworthy and Ethical AI

**Original Spanish:** Inteligencia artificial

**🔍 Vector Search (0.33):** Inteligencia artificial

**✨ LLM Repair:** 7: Sobre Inteligencia Artificial Fiable y Ética ±

**Confidence:** 0.30181941390037537

---

### Issue 300 ✅ FIXED

**English:** 1.  Quoted in D. Palmer, “AI Could Help Solve Humanity’s Biggest Issues by Taking Over from Scientists, Says DeepMind CEO,” Computing, May 26, 2015, www.computing.co.uk/ctg/news/2410022/ai-could-help-...

**Original Spanish:** Melanie Mitchell separa la ciencia real de la ciencia ficción en este amplio examen del estado actual de la IA y de cómo está rehaciendo nuestro mundo.

**🔍 Vector Search (0.54):** Melanie Mitchell separa la ciencia real de la ciencia ficción en este amplio examen del estado actual de la IA y de cómo está rehaciendo nuestro mundo.

**✨ LLM Repair:** "Según lo informado por D. Palmer en 'AI Could Help Solve Humanity’s Biggest Issues by Taking Over from Scientists, Says DeepMind CEO', Computing, 26 de mayo de 2015, www.computing.co.uk/ctg/news/2410...

**Confidence:** 0.41242408752441406

---

### Issue 301 ✅ FIXED

**English:** 2.  S. Lynch, “Andrew Ng: Why AI Is the New Electricity,” Insights by Stanford Business, March 11, 2017, www.gsb.stanford.edu/insights/andrew-ng-why-ai-new-electricity.

**Original Spanish:** Ninguna empresa científica reciente ha resultado tan seductora, aterradora y llena de extravagantes promesas y frustrantes reveses como la inteligencia artificial. La galardonada autora Melanie Mitche...

**🔍 Vector Search (0.50):** Ninguna empresa científica reciente ha resultado tan seductora, aterradora y llena de extravagantes promesas y frustrantes reveses como la inteligencia artificial. La galardonada autora Melanie Mitche...

**✨ LLM Repair:** "2. S. Lynch, "Andrew Ng: ¿Por qué el aprendizaje automático es la nueva electricidad?", Insights by Stanford Business, 11 de marzo de 2017, www.gsb.stanford.edu/insights/andrew-ng-why-ai-new-electric...

**Confidence:** 0.39039844274520874

---

### Issue 302 ✅ FIXED

**English:** 6.  H. Hodson, “Face Recognition Row over Right to Identify You in the Street,” New Scientist, June 19, 2015.

**Original Spanish:** Este libro franco y animado es una guía indispensable para entender la IA actual, su búsqueda de una inteligencia "de nivel humano" y su impacto en el futuro de todos nosotros.

**🔍 Vector Search (0.44):** Este libro franco y animado es una guía indispensable para entender la IA actual, su búsqueda de una inteligencia "de nivel humano" y su impacto en el futuro de todos nosotros.

**✨ LLM Repair:** "6. H. Hodson, 'Controversia en el Reconocimiento Facial sobre el Derecho a Identificarle en la Calle', Nueva Científica, 19 de junio de 2015." ±

**Confidence:** 0.4399108588695526

---

### Issue 303 ✅ FIXED

**English:** 8.  B. Brackeen, “Facial Recognition Software Is Not Ready for Use by Law Enforcement,” Tech Crunch, June 25, 2018, techcrunch.com/2018/06/25/facial-recognition-software-is-not-ready-for-use-by-law-en...

**Original Spanish:** -The New Yorker

**🔍 Vector Search (0.45):** -The New Yorker

**✨ LLM Repair:** "El software de reconocimiento facial no está listo para su uso por las fuerzas del orden", TechCrunch, 25 de junio de 2018, techcrunch.com/2018/06/25/facial-recognition-software-is-not-ready-for-use-...

**Confidence:** 0.22806483507156372

---

### Issue 304 ✅ FIXED

**English:** 9.  B. Smith, “Facial Recognition Technology: The Need for Public Regulation and Corporate Responsibility,” Microsoft on the Issues (blog), Microsoft, July 13, 2018, blogs.microsoft.com/on-the-issues/...

**Original Spanish:** (empty)

**🆕 LLM Generated:** 9. B. Smith, "La tecnología de reconocimiento facial: la necesidad de regulación pública y responsabilidad corporativa", Microsoft en cuestiones (blog), Microsoft, 13 de julio de 2018, blogs.microsoft...

**Confidence:** 0.05

---

### Issue 305 ✅ FIXED

**English:** 10.  K. Walker, “AI for Social Good in Asia Pacific,” Around the Globe (blog), Google, Dec. 13, 2018, www.blog.google/around-the-globe/google-asia/ai-social-good-asia-pacific.

**Original Spanish:** (empty)

**🆕 LLM Generated:** 10. K. Walker, "IA para el bien social en Asia Pacífico", Alrededor del Mundo (blog), Google, 13 de diciembre de 2018, www.blog.google/alrededor-del-mundo/google-asia/ia-bien-social-asia-pacificico. ±

**Confidence:** 0.05

---

### Issue 306 ✅ FIXED

**English:** 11.  B. Goodman and S. Flaxman, “European Union Regulations on Algorithmic Decision-Making and a ‘Right to Explanation,’” AI Magazine 38, no. 3 (Fall 2017): 50–57.

**Original Spanish:** (empty)

**🆕 LLM Generated:** "11. B. Goodman y S. Flaxman, “Regulaciones de la Unión Europea sobre la toma de decisiones algorítmica y el ‘derecho a una explicación,’” Revista AI Magazine 38, no. 3 (Otoño 2017): 50-57." ±

**Confidence:** 0.05

---

### Issue 307 ✅ FIXED

**English:** 12.  “Article 12, EU GDPR: Transparent Information, Communication, and Modalities for the Exercise of the Rights of the Data Subject,” EU General Data Protection Regulation, accessed Dec. 7, 2018, www...

**Original Spanish:** (empty)

**🆕 LLM Generated:** "Artículo 12, Reglamento general de protección de datos de la UE (RGPD): Información transparente, comunicación y modalidades para el ejercicio de los derechos del titular de los datos", acceso el 7 d...

**Confidence:** 0.05

---

### Issue 308 ✅ FIXED

**English:** 13.  Partnership on AI website, accessed Dec. 18, 2018, www.partnershiponai.org.

**Original Spanish:** (empty)

**🆕 LLM Generated:** Sitio web de la Asociación por el Avance de la Inteligencia Artificial, consultado el 18 de diciembre de 2018, www.asociacionporlaia.org. ±

**Confidence:** 0.05

---

### Issue 309 ✅ FIXED

**English:** 14.  For an extended survey of this topic, see W. Wallach and C. Allen, Moral Machines: Teaching Robots Right from Wrong (New York: Oxford University Press, 2008).

**Original Spanish:** (empty)

**🆕 LLM Generated:** Para un estudio más amplio de este tema, consulte a W. Wallach y C. Allen, Máquinas Morales: Enseñando a los Robots el Bien del Mal (Nueva York: Universidad de Oxford Press, 2008). ±

**Confidence:** 0.05

---

### Issue 310 ✅ FIXED

**English:** 15.  I. Asimov, I, Robot (Bantam Dell, 2004), 37. (First edition: Grove, 1950.)

**Original Spanish:** (empty)

**🆕 LLM Generated:** 15. Isaac Asimov, "Yo, robot" (Bantam Dell, 2004), 37. (Primera edición: Grove, 1950.) ±

**Confidence:** 0.05

---

### Issue 311 ✅ FIXED

**English:** 16.  A. C. Clarke, 2001: A Space Odyssey (London: Hutchinson & Co, 1968).

**Original Spanish:** (empty)

**🆕 LLM Generated:** "A. C. Clarke, 2001: Odisea del Espacio (Londres: Hutchinson & Co, 1968)." ±

**Confidence:** 0.05

---

### Issue 312 ✅ FIXED

**English:** 19.  J. J. Thomson, “The Trolley Problem,” Yale Law Journal 94, no. 6 (1985): 1395–415.

**Original Spanish:** -George Musser.

**🔍 Vector Search (0.44):** -George Musser.

**✨ LLM Repair:** 19. J. J. Thomson, "El Problema del Tranvía", Yale Law Journal 94, n.º 6 (1985): 1395-415. ±

**Confidence:** 0.32026928663253784

---

### Issue 313 ✅ FIXED

**English:** 20.  For example, see J. Achenbach, “Driverless Cars Are Colliding with the Creepy Trolley Problem,” Washington Post, December 29, 2015.

**Original Spanish:** (empty)

**🆕 LLM Generated:** Para ilustrar esto, véase J. Achenbach, "Los coches autónomos se enfrentan al problema del trolley espeluznante", The Washington Post, 29 de diciembre de 2015. ±

**Confidence:** 0.05

---

### Issue 314 ✅ FIXED

**English:** 21.  J.-F. Bonnefon, A. Shariff, and I. Rahwan, “The Social Dilemma of Autonomous Vehicles,” Science 352, no. 6293 (2016): 1573–76.

**Original Spanish:** (empty)

**🆕 LLM Generated:** "21. J.-F. Bonnefon, A. Shariff e I. Rahwan, “El Dilema Social de los Vehículos Autónomos”, Ciencia 352, no. 6293 (2016): 1573–76." ±

**Confidence:** 0.05

---

### Issue 315 ✅ FIXED

**English:** 22.  J. D. Greene, “Our Driverless Dilemma,” Science 352, no. 6293 (2016): 1514–15.

**Original Spanish:** (empty)

**🆕 LLM Generated:** "El problema de nuestros vehículos sin conductor", Ciencia 352, no. 6293 (2016): 1514-15. ±

**Confidence:** 0.05

---

### Issue 316 ✅ FIXED

**English:** 23.  For example, see M. Anderson and S. L. Anderson, “Machine Ethics: Creating an Ethical Intelligent Agent,” AI Magazine 28, no. 4 (2007): 15.

**Original Spanish:** (empty)

**🆕 LLM Generated:** Por ejemplo, véase M. Anderson y S. L. Anderson, "Ética de las máquinas: Creando un agente inteligente ético", Revista de IA 28, no. 4 (2007): 15. ±

**Confidence:** 0.05

---

### Issue 317 📏 OVER-LONG (FIXED)

**English:** 3.  To be more precise, this approach to reinforcement learning, called value learning, is not the only possible approach. A second approach, called policy learning, has the goal of learning directly ...

**Original Spanish:** Las empresas que desarrollan la tecnología de vehículos autónomos son muy conscientes del problema d...

**📏 LLM Resized:** 3. Para ser más precisos, esta aproximación al aprendizaje por refuerzo, conocida como aprendizaje de valor, no es la única posible. Una segunda aproximación, llamada aprendizaje de política, tiene co...

**Confidence:** 0.15

---

### Issue 318 📏 OVER-LONG (FIXED)

**English:** 4.  C. J. Watkins and P. Dayan, “Q-Learning,” Machine Learning 8, nos. 3–4 (1992): 279–92.

**Original Spanish:** Los humanos cometen errores constantemente, incluso (o especialmente) al volante; cualquiera de noso...

**📏 LLM Resized:** "4. C.J. Watkins y P. Dayan, “Aprendizaje por reforzamiento con Q-Learning”, Máquinas de Aprendizaje 8, números 3-4 (1992): 279-92." ±

**Confidence:** 0.15

---

### Issue 319 ✅ FIXED

**English:** 5.  For a detailed, technical introduction to reinforcement learning, see R. S. Sutton and A. G. Barto, Reinforcement Learning: An Introduction, 2nd ed. (Cambridge, Mass.: MIT Press, 2017), incomplete...

**Original Spanish:** ¿Qué ha aprendido mi red?

**🔍 Vector Search (0.50):** ¿Qué ha aprendido mi red?

**✨ LLM Repair:** Para una introducción detallada y técnica al aprendizaje por refuerzo, consulte R. S. Sutton y A. G. Barto, Aprendizaje por refuerzo: Una introducción (Cambridge, Mass.: MIT Press, 2017), incompleteid...

**Confidence:** 0.30592602491378784

---

### Issue 320 📏 OVER-LONG (FIXED)

**English:** 6.  For example, see the following papers: P. Christiano et al., “Transfer from Simulation to Real World Through Learning Deep Inverse Dynamics Model,” arXiv:1610.03518 (2016); J. P. Hanna and P. Ston...

**Original Spanish:** Hace unos años, Will Landecker, entonces estudiante de posgrado en mi grupo de investigación, entren...

**📏 LLM Resized:** 6. Por ejemplo, véase los siguientes artículos: P. Christiano et al., "Transferencia desde la simulación al mundo real a través del aprendizaje de modelos profundos de dinámica inversa", arXiv:1610.03...

**Confidence:** 0.15

---

### Issue 321 ✅ FIXED

**English:** 2.  Quoted in “From Not Working to Neural Networking,” Economist, June 25, 2016.

**Original Spanish:** Y, al contrario, muchas cosas que a los humanos nos parecerían horrorosamente difíciles (por ejemplo, multiplicar correctamente dos números de cincuenta cifras) las hacen los ordenadores en una fracci...

**🔍 Vector Search (0.26):** Y, al contrario, muchas cosas que a los humanos nos parecerían horrorosamente difíciles (por ejemplo, multiplicar correctamente dos números de cincuenta cifras) las hacen los ordenadores en una fracci...

**✨ LLM Repair:** "No trabajado a conectado neuronal," El economista, 25 de junio del 2016. ±

**Confidence:** 0.25886857509613037

---

### Issue 322 ✅ FIXED

**English:** 4.  More technically, DeepMind’s program used what is called an epsilon-greedy method for choosing an action at each time step. With probability epsilon the program chooses an action at random; with p...

**Original Spanish:** El algoritmo que más sorprendió por sus buenos resultados fue el de «búsqueda aleatoria»: en lugar de entrenar una red Q profunda mediante aprendizaje por refuerzo durante muchos episodios, es posible...

**🔍 Vector Search (0.45):** El algoritmo que más sorprendió por sus buenos resultados fue el de «búsqueda aleatoria»: en lugar de entrenar una red Q profunda mediante aprendizaje por refuerzo durante muchos episodios, es posible...

**✨ LLM Repair:** 4. En términos más técnicos, el programa de DeepMind utilizó un método llamado ε-greedy para elegir una acción en cada paso de tiempo. Con una probabilidad ε, el programa eligió una acción al azar; co...

**Confidence:** 0.38336655497550964

---

### Issue 323 ✅ FIXED

**English:** 5.  R. S. Sutton and A. G. Barto, Reinforcement Learning: An Introduction, 2nd ed. (Cambridge, Mass.: MIT Press, 2017), 124, incompleteideas.net/book/the-book-2nd.html.

**Original Spanish:** (empty)

**🆕 LLM Generated:** "5. R.S. Sutton y A.G. Barto, Aprendizaje por refuerzo: una introducción, 2.ª ed. (Cambridge, Mass.: Editorial MIT, 2017), página 124, incompleteideas.net/libro/the-book-2nd.html." ±

**Confidence:** 0.05

---

### Issue 324 ✅ FIXED

**English:** 6.  For more details, see V. Mnih et al., “Human-Level Control Through Deep Reinforcement Learning,” Nature 518, no. 7540 (2015): 529.

**Original Spanish:** (empty)

**🆕 LLM Generated:** Para más detalles, véase V. Mnih et al., "Control en el nivel humano a través del aprendizaje profundo por refuerzo", Naturaleza 518, nº 7540 (2015): 529. ±

**Confidence:** 0.05

---

### Issue 325 📏 OVER-LONG (FIXED)

**English:** 7.  V. Mnih et al., “Playing Atari with Deep Reinforcement Learning,” Proceedings of the Neural Information Processing Systems (NIPS) Conference, Deep Learning Workshop (2013).

**Original Spanish:** Podría parecer que una red con pesos aleatorios tendría unos resultados horribles en un videojuego d...

**📏 LLM Resized:** 7. V. Mnih et al., "Jugar Atari con aprendizaje profundo mediante aprendizaje por refuerzo", Actas de la Conferencia sobre Procesamiento de Información Neural (NIPS), Taller de Aprendizaje Profundo (2...

**Confidence:** 0.15

---

### Issue 326 ✅ FIXED

**English:** 9.  Samuel’s program used a variable number of plies, depending on the move.

**Original Spanish:** ¿Qué aprendieron estos sistemas?

**🔍 Vector Search (0.22):** ¿Qué aprendieron estos sistemas?

**✨ LLM Repair:** 9. El programa de Samuel utilizaba un número variable de capas, dependiendo del movimiento. ±

**Confidence:** 0.21479375660419464

---

### Issue 327 ✅ FIXED

**English:** 11.  For details, see A. L. Samuel, “Some Studies in Machine Learning Using the Game of Checkers,” IBM Journal of Research and Development 3, no. 3 (1959): 210–29.

**Original Spanish:** (empty)

**🆕 LLM Generated:** Para más detalles, véase A. L. Samuel, "Algunos estudios sobre aprendizaje automático utilizando el juego de damas", IBM Journal of Research and Development 3, no. 3 (1959): 210-29. ±

**Confidence:** 0.05

---

### Issue 328 ✅ FIXED

**English:** 13.  J. Schaeffer et al., “CHINOOK: The World Man-Machine Checkers Champion,” AI Magazine 17, no. 1 (1996): 21.

**Original Spanish:** (empty)

**🆕 LLM Generated:** 13. J. Schaeffer et al., "CHINOOK: El campeón mundial hombre-máquina de ajedrez", Revista de IA 17, n.º 1 (1996): 21. ±

**Confidence:** 0.05

---

### Issue 329 ✅ FIXED

**English:** 14.  D. Hassabis, “Artificial Intelligence: Chess Match of the Century,” Nature 544 (2017): 413–14.

**Original Spanish:** (empty)

**🆕 LLM Generated:** En el siglo XXI, la inteligencia artificial se enfrenta en una partida de ajedrez que marcará un hito en la historia de esta milenaria disciplina. Dos gigantes digitales, AlphaZero de DeepMind y Stock...

**Confidence:** 0.05

---

### Issue 330 ✅ FIXED

**English:** 15.  A. Newell, J. Calman Shaw, and H. A. Simon, “Chess-Playing Programs and the Problem of Complexity,” IBM Journal of Research and Development 2, no. 4 (1958): 320–35.

**Original Spanish:** (empty)

**🆕 LLM Generated:** "15. A. Newell, J. Calman Shaw y H. A. Simon, “Programas de ajedrez y el problema de la complejidad”, IBM Journal of Research and Development 2, no. 4 (1958): 320–35." ±

**Confidence:** 0.05

---

### Issue 331 ✅ FIXED

**English:** 16.  M. Newborn, Deep Blue: An Artificial Intelligence Milestone (New York: Springer, 2003), 236.

**Original Spanish:** (empty)

**🆕 LLM Generated:** 16. M. Nuevo nacido, Profundo Azul: Hito de Inteligencia Artificial (Nueva York: Springer, 2003), 236. ±

**Confidence:** 0.05

---

### Issue 332 ✅ FIXED

**English:** 17.  Quoted in J. Goldsmith, “The Last Human Chess Master,” Wired, Feb. 1, 1995.

**Original Spanish:** (empty)

**🆕 LLM Generated:** "Citado en J. Goldsmith, «El último maestro humano del ajedrez», Wired, 1 de febrero de 1995." ±

**Confidence:** 0.05

---

### Issue 333 ✅ FIXED

**English:** 18.  Quoted in M. Y. Vardi, “Artificial Intelligence: Past and Future,” Communications of the Association for Computing Machinery 55, no. 1 (2012): 5.

**Original Spanish:** Es peligrosamente fácil, para mí y para cualquiera, caer en este tipo de lenguaje al hablar del comportamiento de los sistemas de IA. Sin embargo, incluye muchas veces suposiciones inconscientes que p...

**🔍 Vector Search (0.40):** Es peligrosamente fácil, para mí y para cualquiera, caer en este tipo de lenguaje al hablar del comportamiento de los sistemas de IA. Sin embargo, incluye muchas veces suposiciones inconscientes que p...

**✨ LLM Repair:** En la obra "Inteligencia Artificial: Pasado y Futuro", de M. Y. Vardi, publicada en las Comunicaciones de la Asociación para Maquinaria de Computación 55, número 1 del año 2012. ±

**Confidence:** 0.3255450427532196

---

### Issue 334 ✅ FIXED

**English:** 19.  A. Levinovitz, “The Mystery of Go, the Ancient Game That Computers Still Can’t Win,” Wired, May 12, 2014.

**Original Spanish:** Gary Marcus nos recuerda que debemos tener cuidado con estas cosas:

**🔍 Vector Search (0.41):** Gary Marcus nos recuerda que debemos tener cuidado con estas cosas:

**✨ LLM Repair:** 19. A. Levinovitz, "El misterio de Go, el juego antiguo que los ordenadores aún no pueden ganar", Wired, 12 de mayo de 2014. ±

**Confidence:** 0.318368136882782

---

### Issue 335 📏 OVER-LONG (FIXED)

**English:** 20.  G. Johnson, “To Test a Powerful Computer, Play an Ancient Game,” New York Times, July 29, 1997.

**Original Spanish:** El sistema no ha aprendido nada de eso; no entiende realmente qué es un túnel ni qué es un muro; no ...

**📏 LLM Resized:** El juego de la oca es un juego antiguo y popular que ha sido jugado por siglos en Europa y América Latina. Aunque no tiene un origen claro, se cree que surgió en España durante el siglo XVI. El juego ...

**Confidence:** 0.15

---

### Issue 336 📏 OVER-LONG (FIXED)

**English:** 21.  Quoted in “S. Korean Go Player Confident of Beating Google’s AI,” Yonhap News Agency, Feb. 23, 2016, english.yonhapnews.co.kr/search1/2603000000.html?cid=AEN20160223003651315.

**Original Spanish:** Marcus se está refiriendo a varios estudios que intentaron averiguar hasta qué punto los sistemas de...

**📏 LLM Resized:** "Citado en 'Jugador de Go coreano confía en vencer a la IA de Google', Agencia de Noticias Yonhap, 23 de febrero de 2016, english.yonhapnews.co.kr/search1/2603000000.html?cid=AEN20160223003651315." ±

**Confidence:** 0.15

---

### Issue 337 ✅ FIXED

**English:** 24.  “For Artificial Intelligence to Thrive, It Must Explain Itself,” Economist, Feb. 15, 2018, www.economist.com/news/science-and-technology/21737018-if-it-cannot-who-will-trust-it-artificial-intelli...

**Original Spanish:** (empty)

**🆕 LLM Generated:** "Para que la Inteligencia Artificial prospere, debe explicarse a sí misma," Economista, 15 de febrero de 2018, www.economist.com/noticias/cienicas-y-tecnologia/21737018-si-no-lo-hace-quien-confiará-en...

**Confidence:** 0.05

---

### Issue 338 📏 OVER-LONG (FIXED)

**English:** 25.  P. Taylor, “The Concept of ‘Cat Face,’” London Review of Books, Aug. 11, 2016.

**Original Spanish:** Estas demostraciones dejan claro que es equívoco atribuir al aprendizaje por refuerzo profundo la in...

**📏 LLM Resized:** 25. P. Taylor, "El concepto de 'Carita de gato'", London Review of Books, 11 de agosto de 2016. ±

**Confidence:** 0.15

---

### Issue 339 ✅ FIXED

**English:** 27.  D. Silver et al., “Mastering the Game of Go Without Human Knowledge,” Nature, 550 (2017): 354–59.

**Original Spanish:** (empty)

**🆕 LLM Generated:** 27. D. Plata et al., "Dominar el Juego del Go Sin Conocimiento Humano", Naturaleza, 550 (2017): 354-59. ±

**Confidence:** 0.05

---

### Issue 340 ✅ FIXED

**English:** 28.  D. Silver et al., “A General Reinforcement Learning Algorithm That Masters Chess, Shogi, and Go Through Self-Play,” Science 362, no. 6419 (2018): 1140–44.

**Original Spanish:** En definitiva, aunque estos sistemas profundos de aprendizaje Q han logrado un rendimiento sobrehumano en algunas áreas concretas, e incluso muestran algo parecido a la «intuición» en esos terrenos, l...

**🔍 Vector Search (0.45):** En definitiva, aunque estos sistemas profundos de aprendizaje Q han logrado un rendimiento sobrehumano en algunas áreas concretas, e incluso muestran algo parecido a la «intuición» en esos terrenos, l...

**✨ LLM Repair:** "28. D. Silver et al., “Un algoritmo general de aprendizaje por refuerzo que domina ajedrez, shogi y go mediante el juego propio”, Ciencia 362, no. 6419 (2018): 1140-44." ±

**Confidence:** 0.36393803358078003

---

### Issue 341 ✅ FIXED

**English:** 1.  Quoted in P. Iwaniuk, “A Conversation with Demis Hassabis, the Bullfrog AI Prodigy Now Finding Solutions to the World’s Big Problems,” PCGamesN, accessed Dec. 7, 2018, www.pcgamesn.com/demis-hassa...

**Original Spanish:** (empty)

**🆕 LLM Generated:** "Citado en P. Iwaniuk, “Una conversación con Demis Hassabis, el prodigio de Inteligencia Artificial Bullfrog ahora buscando soluciones a los problemas del mundo”, PCGamesN, consultado el 7 de diciembr...

**Confidence:** 0.05

---

### Issue 342 ✅ FIXED

**English:** 2.  E. David, “DeepMind’s AlphaGo Mastered Chess in Its Spare Time,” Silicon Angle, Dec. 6, 2017, siliconangle.com/blog/2017/12/06/deepminds-alphago-mastered-chess-spare-time.

**Original Spanish:** ¿Cómo de inteligente es AlphaGo?

**🔍 Vector Search (0.45):** ¿Cómo de inteligente es AlphaGo?

**✨ LLM Repair:** 2. E. David, "AlphaGo de DeepMind dominó el ajedrez en su tiempo libre", Silicon Angle, 6 de diciembre de 2017, siliconangle.com/blog/2017/12/06/deepminds-alphago-mastered-chess-spare-time. ±

**Confidence:** 0.44998547434806824

---

### Issue 343 ✅ FIXED

**English:** 3.  As one example, still in the game-playing domain, DeepMind published a paper in 2018 describing a reinforcement-learning system that they claimed exhibited some degree of transfer learning in its ...

**Original Spanish:** Hay algo que debemos tener en cuenta cuando hablamos de juegos como el ajedrez y el go y su relación con la inteligencia humana. Pensemos en los motivos por los que muchos padres animan a sus hijos a ...

**🔍 Vector Search (0.62):** Todos estos problemas llevaron a Andrej Karpathy, director de IA de Tesla, a señalar que para tareas del mundo real como esta, «básicamente se quiebran todos y cada uno de los supuestos que cumple el ...

**Confidence:** 0.4168311059474945

---

### Issue 344 📏 OVER-LONG (FIXED)

**English:** 4.  D. Silver et al., “Mastering the Game of Go Without Human Knowledge,” Nature 550 (2017): 354–59.

**Original Spanish:** En cambio, AlphaGo, a pesar de los millones de partidas que ha jugado durante su entrenamiento, no h...

**📏 LLM Resized:** 4. D. Plata et al., "Domando el juego del Go sin conocimiento humano", Naturaleza 550 (2017): 354-59. ±

**Confidence:** 0.15

---

### Issue 345 ✅ FIXED

**English:** 5.  G. Marcus, “Innateness, AlphaZero, and Artificial Intelligence,” arXiv:1801.05667 (2018).

**Original Spanish:** Desde luego, el método de aprendizaje Q profundo utilizado en AlphaGo puede servir para aprender otras tareas, pero el sistema tendría que volver a hacer todo el entrenamiento; tendría que empezar bás...

**🔍 Vector Search (0.45):** Desde luego, el método de aprendizaje Q profundo utilizado en AlphaGo puede servir para aprender otras tareas, pero el sistema tendría que volver a hacer todo el entrenamiento; tendría que empezar bás...

**✨ LLM Repair:** "5. G. Marcus, «Innatez, AlphaZero y la Inteligencia Artificial», arXiv:1801.05667 (2018)." ±

**Confidence:** 0.3856826424598694

---

### Issue 346 ✅ FIXED

**English:** 6.  F. P. Such et al., “Deep Neuroevolution: Genetic Algorithms Are a Competitive Alternative for Training Deep Neural Networks for Reinforcement Learning,” Proceedings of the Neural Information Proce...

**Original Spanish:** Esto nos lleva de nuevo a la paradoja de la IA de que «lo fácil es difícil». AlphaGo fue un gran triunfo para la IA; después de aprender en gran parte a base de jugar contra sí mismo, consiguió derrot...

**🔍 Vector Search (0.56):** Esto nos lleva de nuevo a la paradoja de la IA de que «lo fácil es difícil». AlphaGo fue un gran triunfo para la IA; después de aprender en gran parte a base de jugar contra sí mismo, consiguió derrot...

**✨ LLM Repair:** 6. F.P. Such et al., "Evolución Neurod profunda: los algoritmos genéticos son una alternativa competitiva para el entrenamiento de redes neuronales profundas en aprendizaje por refuerzo", Taller de Ap...

**Confidence:** 0.39601433277130127

---

### Issue 347 ✅ FIXED

**English:** 7.  M. Mitchell, An Introduction to Genetic Algorithms (Cambridge, Mass.: MIT Press, 1996).

**Original Spanish:** De los juegos al mundo real

**🔍 Vector Search (0.41):** De los juegos al mundo real

**✨ LLM Repair:** 7. M. Mitchell, Introducción a los Algoritmos Genéticos (Cambridge, Massachusetts: MIT Press, 1996). ±

**Confidence:** 0.2736608386039734

---

### Issue 348 📏 OVER-LONG (FIXED)

**English:** 8.  Marcus, “Innateness, AlphaZero, and Artificial Intelligence.”

**Original Spanish:** Por último, consideremos la afirmación de Demis Hassabis de que el objetivo verdaderamente important...

**📏 LLM Resized:** "8. Marcus, 'Innatez, AlphaZero y la Inteligencia Artificial.'" ±

**Confidence:** 0.15

---

### Issue 349 📏 OVER-LONG (FIXED)

**English:** 9.  G. Marcus, “Deep Learning: A Critical Appraisal,” arXiv:1801.00631 (2018).

**Original Spanish:** Un obstáculo es la necesidad de transferir el aprendizaje. Pero hay otros motivos por los que será d...

**📏 LLM Resized:** "9. G. Marcus, “Evaluación Crítica del Aprendizaje Profundo”, arXiv: 1801.00631 (2018)."

Note that the tone and style of the original English text have been maintained in the Spanish translation. The...

**Confidence:** 0.15

---

### Issue 350 ✅ FIXED

**English:** 10.  K. Kansky et al., “Schema Networks: Zero-Shot Transfer with a Generative Causal Model of Intuitive Physics,” in Proceedings of the International Conference on Machine Learning (2017), 1809–18.

**Original Spanish:** El mundo real no tiene unos límites tan claros. Douglas Hofstadter ha señalado que la propia noción de un «estado» claramente definido no es nada realista. «Si vemos las situaciones que se dan en el m...

**🔍 Vector Search (0.46):** El mundo real no tiene unos límites tan claros. Douglas Hofstadter ha señalado que la propia noción de un «estado» claramente definido no es nada realista. «Si vemos las situaciones que se dan en el m...

**✨ LLM Repair:** "10. K. Kansky et al., 'Redes de Esquemas: Transferencia en Cero Pasos con un Modelo Causal Generativo de Física Intuitiva', en Actas de la Conferencia Internacional sobre Aprendizaje Automático (2017...

**Confidence:** 0.25336286425590515

---

### Issue 351 📏 OVER-LONG (FIXED)

**English:** 11.  A. A. Rusu et al., “Progressive Neural Networks,” arXiv:1606.04671 (2016).

**Original Spanish:** Por poner un ejemplo, imaginemos el uso del aprendizaje por refuerzo para enseñar a un robot a hacer...

**📏 LLM Resized:** "11. A.A. Rusu, et al., "Redes Neuronales Progresivas", arXiv:1606.04671 (2016)." ±

**Confidence:** 0.15

---

### Issue 352 ✅ FIXED

**English:** 13.  Quoted in N. Sonnad and D. Gershgorn, “Q&A: Douglas Hofstadter on Why AI Is Far from Intelligent,” Quartz, Oct. 10, 2017, qz.com/1088714/qa-douglas-hofstadter-on-why-ai-is-far-from-intelligent.

**Original Spanish:** Todos estos problemas llevaron a Andrej Karpathy, director de IA de Tesla, a señalar que para tareas del mundo real como esta, «básicamente se quiebran todos y cada uno de los supuestos que cumple el ...

**🔍 Vector Search (0.48):** Todos estos problemas llevaron a Andrej Karpathy, director de IA de Tesla, a señalar que para tareas del mundo real como esta, «básicamente se quiebran todos y cada uno de los supuestos que cumple el ...

**✨ LLM Repair:** "13. Citado en N. Sonnad y D. Gershgorn, 'Preguntas y respuestas: Douglas Hofstadter sobre por qué la IA está lejos de ser inteligente', Quartz, 10 de octubre de 2017, qz.com/1088714/pregunta-y-respue...

**Confidence:** 0.43011125922203064

---

### Issue 353 ✅ FIXED

**English:** 15.  A. Karpathy, “AlphaGo, in Context,” Medium, May 31, 2017, medium.com/@karpathy/alphago-in-context-c47718cb95a5.

**Original Spanish:** (empty)

**🆕 LLM Generated:** "15. A. Karpathy, «AlphaGo, en contexto», Medium, 31 de mayo de 2017, medium.com/@karpathy/alphago-en-contexto-c47718cb95a5." ±

**Confidence:** 0.05

---

### Issue 354 ✅ FIXED

**English:** 18.  The idea is to solve for x in the vector arithmetic problem man − woman = king − x. To add or subtract two vectors, just add or subtract their corresponding elements; for example, (3, 2, 4) − (1,...

**Original Spanish:** Figura 18. Ejemplos originales y «antagónicos» para AlexNet. La imagen de la izquierda de cada par muestra la imagen original, correctamente clasificada por AlexNet. La imagen de la derecha de cada pa...

**🔍 Vector Search (0.39):** Figura 18. Ejemplos originales y «antagónicos» para AlexNet. La imagen de la izquierda de cada par muestra la imagen original, correctamente clasificada por AlexNet. La imagen de la derecha de cada pa...

**✨ LLM Repair:** La idea es resolver para x en el problema de álgebra vectorial hombre - mujer = rey - x. Para sumar o restar dos vectores, simplemente suma o resta sus elementos correspondientes; por ejemplo, (3, 2, ...

**Confidence:** 0.39289146661758423

---

### Issue 355 ✅ FIXED

**English:** 20.  R. Kiros et al., “Skip-Thought Vectors,” in Advances in Neural Information Processing Systems 28 (2015), 3294–302.

**Original Spanish:** Figura 20. Un investigador de IA (izquierda) lleva monturas de gafas con un patrón especialmente diseñado para que una red neuronal profunda de reconocimiento facial, entrenada con rostros de famosos,...

**🔍 Vector Search (0.41):** Figura 20. Un investigador de IA (izquierda) lleva monturas de gafas con un patrón especialmente diseñado para que una red neuronal profunda de reconocimiento facial, entrenada con rostros de famosos,...

**✨ LLM Repair:** "20. R. Kiros, et al., "Vectores Skip-Thought", en Avances en procesamiento de información neuronal 28 (2015), 3294-302." ±

**Confidence:** 0.33551275730133057

---

### Issue 356 📏 OVER-LONG (FIXED)

**English:** 11: Words, and the Company They Keep

**Original Spanish:** Los seres humanos tampoco pueden explicar siempre sus procesos mentales, y, en general, no es posibl...

**📏 LLM Resized:** Once palabras, y la compañía que frecuentan ±

**Confidence:** 0.15

---

### Issue 357 ✅ FIXED

**English:** 2.  G. Hinton et al., “Deep Neural Networks for Acoustic Modeling in Speech Recognition: The Shared Views of Four Research Groups,” IEEE Signal Processing Magazine 29, no. 6 (2012): 82–97.

**Original Spanish:** Nadie tiene una «teoría de la mente» similar en relación con sistemas de IA como las redes profundas, por lo que es más difícil confiar en ellos.

**🔍 Vector Search (0.49):** Nadie tiene una «teoría de la mente» similar en relación con sistemas de IA como las redes profundas, por lo que es más difícil confiar en ellos.

**✨ LLM Repair:** "2. G. Hinton et al., 'Redes neuronales profundas para la modelización acústica en el reconocimiento del habla: las visiones compartidas de cuatro grupos de investigación', IEEE Signal Processing Maga...

**Confidence:** 0.4324929118156433

---

### Issue 358 ✅ FIXED

**English:** 3.  J. Dean, “Large Scale Deep Learning,” slides from keynote lecture, Conference on Information and Knowledge Management (CIKM), Nov. 2014, accessed Dec. 7, 2018, static.googleusercontent.com/media/r...

**Original Spanish:** (empty)

**🆕 LLM Generated:** 3. J. Dean, “Aprendizaje Profundo a Gran Escala”, diapositivas de la conferència magistral, Conferència sobre Gestió de l'Informació i el Coneixement (CIKM), novembre del 2014, accedida el 7 de desemb...

**Confidence:** 0.05

---

### Issue 359 ✅ FIXED

**English:** 6.  A good, though technical, overview of how modern speech-recognition algorithms work is given in J.H.L. Hansen and T. Hasan, “Speaker Recognition by Machines and Humans: A Tutorial Review,” IEEE Si...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Una buena aunque técnica revisión de cómo funcionan los algoritmos modernos de reconocimiento del habla se presenta en J.H.L. Hansen y T. Hasan, "Reconocimiento de hablantes por máquinas y humanos: un...

**Confidence:** 0.05

---

### Issue 360 ✅ FIXED

**English:** 7.  These reviews are from Amazon.com; in some cases, I have lightly edited them.

**Original Spanish:** (empty)

**🆕 LLM Generated:** Estas reseñas son de Amazon.com; en algunos casos, las he editado ligeramente. ±

**Confidence:** 0.05

---

### Issue 361 ✅ FIXED

**English:** 8.  At the time of this writing, the online world is still reeling from the news that a data-analytics company called Cambridge Analytica used data from tens of millions of Facebook accounts to help t...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Al momento de la redacción de este texto, el mundo en línea sigue conmocionado por la noticia de que una empresa de análisis de datos llamada Cambridge Analytica utilizó datos de decenas de millones d...

**Confidence:** 0.05

---

### Issue 362 ✅ FIXED

**English:** 9.  Recall from chapter 2 that each unit in a neural network computes a mathematical function of the sum of its inputs times their weights. This can be done only if the inputs are numbers.

**Original Spanish:** Engañar a las redes neuronales profundas

**🔍 Vector Search (0.41):** Engañar a las redes neuronales profundas

**✨ LLM Repair:** Capítulo 2 nos recuerda que cada unidad en una red neuronal calcula una función matemática de la suma de sus entradas multiplicadas por sus pesos. Esto solo es posible si las entradas son números. ±

**Confidence:** 0.2693343758583069

---

### Issue 363 ✅ FIXED

**English:** 10.  J. Firth, “A Synopsis of Linguistic Theory, 1930–1955,” in Studies in Linguistic Analysis (Oxford: Philological Society, 1957), 1–32.

**Original Spanish:** Hay otra dimensión más en la cuestión de la fiabilidad de la IA: los investigadores han descubierto que para los humanos es asombrosamente fácil engañar a las redes neuronales profundas para que comet...

**🔍 Vector Search (0.43):** Hay otra dimensión más en la cuestión de la fiabilidad de la IA: los investigadores han descubierto que para los humanos es asombrosamente fácil engañar a las redes neuronales profundas para que comet...

**✨ LLM Repair:** 10. J. Firth, "Sinopsis de la teoría lingüística, 1930-1955", en Estudios de análisis lingüístico (Oxford: Sociedad Filológica, 1957), 1-32. ±

**Confidence:** 0.4039032459259033

---

### Issue 364 ✅ FIXED

**English:** 11.  A. Lenci, “Distributional Semantics in Linguistic and Cognitive Research,” Italian Journal of Linguistics 20, no. 1 (2008): 1–31.

**Original Spanish:** Engañar a los sistemas de inteligencia artificial no es nuevo. Quienes llenan de spam nuestros correos electrónicos, por ejemplo, llevan décadas en una carrera armamentística con los programas centrad...

**🔍 Vector Search (0.39):** Engañar a los sistemas de inteligencia artificial no es nuevo. Quienes llenan de spam nuestros correos electrónicos, por ejemplo, llevan décadas en una carrera armamentística con los programas centrad...

**✨ LLM Repair:** 11. A. Lenci, "Semántica distributiva en investigación lingüística y cognitiva", Revista de Lingüística Italiana 20, n.º 1 (2008): 1-31. ±

**Confidence:** 0.30445951223373413

---

### Issue 365 ✅ FIXED

**English:** 12.  In physics, the term vector is often defined as an entity having a magnitude and direction. This definition is equivalent to the one I gave in the text: any vector can be uniquely described by th...

**Original Spanish:** ¿Recuerdan AlexNet, de la que hablé en el capítulo 5? Era la red neuronal convolucional que ganó el concurso de ImageNet de 2012 e inició el dominio de las ConvNet en gran parte del mundo de la IA act...

**🔍 Vector Search (0.49):** ¿Recuerdan AlexNet, de la que hablé en el capítulo 5? Era la red neuronal convolucional que ganó el concurso de ImageNet de 2012 e inició el dominio de las ConvNet en gran parte del mundo de la IA act...

**✨ LLM Repair:** En física, el término vector se define a menudo como una entidad que tiene magnitud y dirección. Esta definición es equivalente a la que di en el texto: cualquier vector puede describirse de forma úni...

**Confidence:** 0.3761514127254486

---

### Issue 366 ✅ FIXED

**English:** 13.  T. Mikolov et al., “Efficient Estimation of Word Representations in Vector Space,” in Proceedings of the International Conference on Learning Representations (2013).

**Original Spanish:** (empty)

**🆕 LLM Generated:** 13. T. Mikolov et al., "Estimación eficiente de representaciones de palabras en espacio vectorial", en las Actas de la Conferencia Internacional sobre el Aprendizaje de Representaciones (2013). ±

**Confidence:** 0.05

---

### Issue 367 ✅ FIXED

**English:** 14.  Word2vec, Google Code Archive, code.google.com/archive/p/word2vec/. Word vectors are also called word embeddings.

**Original Spanish:** (empty)

**🆕 LLM Generated:** 14. Vectores de palabras, Archivo de Código de Google, código.google.com/archive/p/word2vec/. También se llaman incrustaciones de palabras. ±

**Confidence:** 0.05

---

### Issue 368 ✅ FIXED

**English:** 15.  Here, I’m illustrating a version of the “skip-gram” method, which was one of two methods proposed in Mikolov et al., “Efficient Estimation of Word Representations in Vector Space.”

**Original Spanish:** En concreto, los autores del artículo habían descubierto que podían coger una foto de ImageNet que AlexNet había clasificado acertadamente y con gran seguridad (por ejemplo, «autobús escolar») y disto...

**🔍 Vector Search (0.44):** En concreto, los autores del artículo habían descubierto que podían coger una foto de ImageNet que AlexNet había clasificado acertadamente y con gran seguridad (por ejemplo, «autobús escolar») y disto...

**✨ LLM Repair:** Aquí presento una variante del método "skip-gram", uno de los dos métodos propuestos en Mikolov et al., "Estimación eficiente de representaciones de palabras en espacio vectorial". ±

**Confidence:** 0.38949960470199585

---

### Issue 369 ✅ FIXED

**English:** 17.  I used the word2vec demo at bionlp-www.utu.fi/wv_demo/ (using “English GoogleNews Negative300” model) to obtain these results.

**Original Spanish:** (empty)

**🆕 LLM Generated:** Usé el demostrador de word2vec en bionlp-www.utu.fi/wv_demo/ (utilizando el modelo "Inglés GoogleNews Negative300") para obtener estos resultados. ±

**Confidence:** 0.05

---

### Issue 370 📏 OVER-LONG (FIXED)

**English:** 24.  For example, see J. Zhao et al., “Learning Gender-Neutral Word Embeddings,” in Proceedings of the 2018 Conference on Empirical Methods in Natural Language Processing (2018), 4847–53, and A. Sutto...

**Original Spanish:** Todo esto ha revitalizado la pequeña comunidad investigadora que se dedica al «aprendizaje antagónic...

**📏 LLM Resized:** Para ilustrar, véase J. Zhao et al., "Aprendizaje de incrustaciones de palabras neutras en cuanto a género", en "Actas de la Conferencia sobre Métodos Empíricos en el Procesamiento del Lenguaje Natura...

**Confidence:** 0.15

---

### Issue 371 ✅ FIXED

**English:** 12: Translation as Encoding and Decoding

**Original Spanish:** Cada problema tiene doce casillas: seis a la izquierda y seis a la derecha.

**🔍 Vector Search (0.32):** Cada problema tiene doce casillas: seis a la izquierda y seis a la derecha.

**✨ LLM Repair:** 12: Traducción como Codificación y Decodificación ±

**Confidence:** 0.23363016545772552

---

### Issue 372 ✅ FIXED

**English:** 1.  Q. V. Le and M. Schuster, “A Neural Network for Machine Translation, at Production Scale,” AI Blog, Google, Sept. 27, 2016, ai.googleblog.com/2016/09/a-neural-network-for-machine.html.

**Original Spanish:** Las seis casillas de la izquierda de cada problema plasman el «mismo» concepto, las seis casillas de la derecha plasman un concepto relacionado, y los dos conceptos diferencian a la perfección los dos...

**🔍 Vector Search (0.46):** Las seis casillas de la izquierda de cada problema plasman el «mismo» concepto, las seis casillas de la derecha plasman un concepto relacionado, y los dos conceptos diferencian a la perfección los dos...

**✨ LLM Repair:** 1. Q.V. Le y M. Schuster, "Una red neuronal para la traducción automática a gran escala", Blog de Inteligencia Artificial, Google, 27 de septiembre de 2016, ai.googleblog.com/2016/09/a-neural-network-...

**Confidence:** 0.3515203595161438

---

### Issue 373 ✅ FIXED

**English:** 2.  W. Weaver, “Translation,” in Machine Translation of Languages, ed. W. N. Locke and A. D. Booth (New York: Technology Press and John Wiley & Sons, 1955), 15–23.

**Original Spanish:** figura 46. Otros seis problemas de Bongard.

**🔍 Vector Search (0.41):** figura 46. Otros seis problemas de Bongard.

**✨ LLM Repair:** En "Traducción", W. Weaver examina la traducción en el contexto de la traducción automática de idiomas. Este texto se encuentra en Machine Translation of Languages, editado por W. N. Locke y A. D. Boo...

**Confidence:** 0.223342165350914

---

### Issue 374 ✅ FIXED

**English:** 3.  This is the method used by Google Translate for most languages. At the time of this writing, Google Translate has not yet switched to neural networks for some less common languages.

**Original Spanish:** Los problemas de la figura 45 son relativamente fáciles de resolver. Bongard organizó sus cien problemas más o menos por orden de dificultad. Si quieren entretenerse, la figura 46 presenta otros seis ...

**🔍 Vector Search (0.36):** Los problemas de la figura 45 son relativamente fáciles de resolver. Bongard organizó sus cien problemas más o menos por orden de dificultad. Si quieren entretenerse, la figura 46 presenta otros seis ...

**✨ LLM Repair:** 3. Este es el método utilizado por Google Translate para la mayoría de los idiomas. En el momento de escribir esto, Google Translate todavía no ha cambiado a redes neuronales para algunos idiomas meno...

**Confidence:** 0.20375487208366394

---

### Issue 375 📏 OVER-LONG (FIXED)

**English:** 4.  For more details, see Y. Wu et al., “Google’s Neural Machine Translation System: Bridging the Gap Between Human and Machine Translation,” arXiv:1609.08144 (2016).

**Original Spanish:** Bongard diseñó cuidadosamente estos rompecabezas de forma que para resolverlos hicieran falta alguna...

**📏 LLM Resized:** Para obtener más detalles, consulte Y. Wu et al., "El sistema de traducción neuronal de Google: Puente entre la traducción humana y mecánica," arXiv:1609.08144 (2016). ±

**Confidence:** 0.15

---

### Issue 376 📏 OVER-LONG (FIXED)

**English:** 5.  In Google’s neural machine-translation system, the word vectors are learned as part of the training of the entire network.

**Original Spanish:** Para descubrir esa sutil igualdad, hay que determinar qué atributos de la situación son relevantes y...

**📏 LLM Resized:** En el sistema de traducción neuronal de Google, los vectores de palabras se aprenden como parte del entrenamiento de la red completa. ±

**Confidence:** 0.15

---

### Issue 377 ✅ FIXED

**English:** 6.  More specifically, the outputs of the decoder network are probabilities for each possible word in the network’s vocabulary (here, French). More details are given in Wu et al., “Google’s Neural Mac...

**Original Spanish:** Para complicar aún más las cosas a las máquinas, los conceptos relevantes pueden codificarse de forma abstracta y difícil de percibir, como pasa con los conceptos tres y cuatro del problema 91. En alg...

**🔍 Vector Search (0.49):** Para complicar aún más las cosas a las máquinas, los conceptos relevantes pueden codificarse de forma abstracta y difícil de percibir, como pasa con los conceptos tres y cuatro del problema 91. En alg...

**✨ LLM Repair:** 6. Más específicamente, las salidas de la red decodificadora son probabilidades para cada palabra posible en el vocabulario de la red (aquí, francés). Para más detalles, véase Wu et al., "El sistema d...

**Confidence:** 0.41611748933792114

---

### Issue 378 ✅ FIXED

**English:** 7.  At the time of this writing, Google Translate and other translation systems work by translating one sentence at a time. An example of research on going beyond sentence-by-sentence translation is d...

**Original Spanish:** Los problemas de Bongard también ponen a prueba nuestra capacidad de percibir nuevos conceptos sobre la marcha. El problema 18 es un buen ejemplo. El concepto común de las casillas de la izquierda no ...

**🔍 Vector Search (0.45):** Los problemas de Bongard también ponen a prueba nuestra capacidad de percibir nuevos conceptos sobre la marcha. El problema 18 es un buen ejemplo. El concepto común de las casillas de la izquierda no ...

**✨ LLM Repair:** 7.  En el momento de la redacción de esto, Google Translate y otros sistemas de traducción funcionan traduciendo un fragmento a la vez. Un ejemplo de investigación sobre ir más allá de la traducción d...

**Confidence:** 0.3737711012363434

---

### Issue 379 ✅ FIXED

**English:** 8.  S. Hochreiter and J. Schmidhuber, “Long Short-Term Memory,” Neural Computation 9, no. 8 (1997): 1735–80.

**Original Spanish:** El libro de Bongard, publicado en inglés en 1970, era bastante arduo y, al principio, poca gente supo de su existencia. Sin embargo, Douglas Hofstadter, que se había encontrado con el libro en 1975, q...

**🔍 Vector Search (0.44):** El libro de Bongard, publicado en inglés en 1970, era bastante arduo y, al principio, poca gente supo de su existencia. Sin embargo, Douglas Hofstadter, que se había encontrado con el libro en 1975, q...

**✨ LLM Repair:** 8. S. Hochreiter y J. Schmidhuber, "Memoria a Largo Plazo", Computación Neural 9, no. 8 (1997): 1735-80. ±

**Confidence:** 0.37688201665878296

---

### Issue 380 📏 OVER-LONG (FIXED)

**English:** 9.	Wu et al., “Google’s Neural Machine Translation System.”

**Original Spanish:** Desde niña, siempre me han gustado los rompecabezas, especialmente los que tienen que ver con la lóg...

**📏 LLM Resized:** 9. Wu et al., "El sistema de traducción neuronal de Google". ±

**Confidence:** 0.15

---

### Issue 381 ✅ FIXED

**English:** 12.  A. Linn, “Microsoft Reaches a Historic Milestone, Using AI to Match Human Performance in Translating News from Chinese to English,” AI Blog, Microsoft, March 14, 2018, blogs.microsoft.com/ai/mach...

**Original Spanish:** Figura 47. Una ilustración de cómo un problema de Bongard podría plantearse como un problema de clasificación, con doce ejemplos de entrenamiento y un nuevo ejemplo de «prueba».

**🔍 Vector Search (0.39):** Figura 47. Una ilustración de cómo un problema de Bongard podría plantearse como un problema de clasificación, con doce ejemplos de entrenamiento y un nuevo ejemplo de «prueba».

**✨ LLM Repair:** 12. A. Linn, "Microsoft alcanza un hito histórico al utilizar IA para igualar el rendimiento humano en la traducción de noticias del chino al inglés", AI Blog, Microsoft, 14 de marzo de 2018, blogs.mi...

**Confidence:** 0.2802727222442627

---

### Issue 382 ✅ FIXED

**English:** 14.  A. Packer, “Understanding the Language of Facebook,” EmTech Digital video lecture, May 23, 2016, events.technologyreview.com/video/watch/alan-packer-understanding-language.

**Original Spanish:** Símbolos activos y construcción de analogías

**🔍 Vector Search (0.36):** Símbolos activos y construcción de analogías

**✨ LLM Repair:** "14. A. Packer, 'Entendiendo el Lenguaje de Facebook', lección magistral en vídeo EmTech Digital, 23 de mayo de 2016, eventos.technologyreview.com/video/mirar/alan-packer-entendiendo-lenguaje." ±

**Confidence:** 0.14777086675167084

---

### Issue 383 ✅ FIXED

**English:** 16.  K. Papineni et al., “BLEU: A Method for Automatic Evaluation of Machine Translation,” in Proceedings of the 40th Annual Meeting of the Association for Computational Linguistics (2002), 311–18.

**Original Spanish:** problema 1: Supongamos que la cadena de letras abc se cambia por abd. ¿Cómo se cambiaría la cadena pqrs según «la misma regla»?

**🔍 Vector Search (0.36):** problema 1: Supongamos que la cadena de letras abc se cambia por abd. ¿Cómo se cambiaría la cadena pqrs según «la misma regla»?

**✨ LLM Repair:** "16. K. Papineni, et al., 'BLEU: un método para la evaluación automática de traducción mecánica', en las Actas de la 40.ª Reunión Anual de la Asociación para la Lingüística Computacional (2002), pp. 3...

**Confidence:** 0.29454898834228516

---

### Issue 384 ✅ FIXED

**English:** 17.  Wu et al., “Google’s Neural Machine Translation System”; H. Hassan et al., “Achieving Human Parity on Automatic Chinese to English News Translation,” arXiv:1803.05567 (2018).

**Original Spanish:** La mayoría de la gente responde «pqrt», porque deduce una regla que es más o menos «sustituir la letra más a la derecha por la que la sucede en el abecedario». Por supuesto, se podrían inferir otras r...

**🔍 Vector Search (0.41):** La mayoría de la gente responde «pqrt», porque deduce una regla que es más o menos «sustituir la letra más a la derecha por la que la sucede en el abecedario». Por supuesto, se podrían inferir otras r...

**✨ LLM Repair:** "17. Wu et al., “Sistema de traducción neuronal de Google”; H. Hassan et al., “Lograr la paridad humana en la traducción automática chino-inglés de noticias”, arXiv:1803.05567 (2018)." ±

**Confidence:** 0.39091575145721436

---

### Issue 385 ✅ FIXED

**English:** 18.  Google Translate’s French translation of the “Restaurant” story: Un homme est entré dans un restaurant et a commandé un hamburger, cuit rare. Quand il est arrivé, il a été brûlé à un croustillant...

**Original Spanish:** pqrd: «Sustituir la letra más a la derecha por d».

**🔍 Vector Search (0.44):** pqrd: «Sustituir la letra más a la derecha por d».

**✨ LLM Repair:** 18. Tradución de Google Translate del relato "Restaurant" al francés: Un hombre entró en un restaurante y pidió un hamburguesa, cocido raro. Cuando llegó, estaba quemado hasta un crujiente. La camarer...

**Confidence:** 0.3042649030685425

---

### Issue 386 ✅ FIXED

**English:** 19.  Google Translate’s Italian translation of the “Restaurant” story: Un uomo andò in un ristorante e ordinò un hamburger, cucinato raro. Quando è arrivato, è stato bruciato per un croccante. La came...

**Original Spanish:** pqrs: «Sustituir todas las c por d. En pqrs no hay c, así que no cambia nada».

**🔍 Vector Search (0.46):** pqrs: «Sustituir todas las c por d. En pqrs no hay c, así que no cambia nada».

**✨ LLM Repair:** 19. Tradución de Google de "El restaurante" al italiano: Un hombre entró en un restaurante y pidió un hamburger, cocinado raro. Cuando llegó, estaba quemado para un crujiente. La camarera se paró junt...

**Confidence:** 0.35254019498825073

---

### Issue 387 ✅ FIXED

**English:** 20.  Google Translate’s Chinese translation of the “Restaurant” story: 一名男子走进一家餐厅, 点了一个罕见的汉堡包. 当它到达时, 它被烧得脆脆. 女服务员停在男人的桌子旁边. “汉堡好吗” 她问. “哦, 这太好了,” 那男人说, 推开椅子, 没有付钱就冲出餐厅. 女服务员大声喊道：“嘿, 账单呢?” 她耸了耸, 低声嘀咕道...

**Original Spanish:** abd: «Sustituir cualquier cadena por la cadena abd».

**🔍 Vector Search (0.44):** abd: «Sustituir cualquier cadena por la cadena abd».

**✨ LLM Repair:** Un hombre entró en un restaurante y ordenó un hamburguesa poco común. Cuando llegó, estaba muy quemado. La mesera se detuvo junto a la mesa del hombre. "¿Cómo está el hamburguesa?", preguntó. "Oh, est...

**Confidence:** 0.28488191962242126

---

### Issue 388 ✅ FIXED

**English:** 21.  For an in-depth discussion of the problems associated with Google Translate’s lack of understanding, see D. R. Hofstadter, “The Shallowness of Google Translate,” The Atlantic, Jan. 30, 2018.

**Original Spanish:** Estas respuestas alternativas pueden parecer demasiado literales, pero no hay ningún argumento estrictamente lógico que diga que están mal. De hecho, se podrían deducir infinitas reglas posibles. ¿Por...

**🔍 Vector Search (0.47):** Estas respuestas alternativas pueden parecer demasiado literales, pero no hay ningún argumento estrictamente lógico que diga que están mal. De hecho, se podrían deducir infinitas reglas posibles. ¿Por...

**✨ LLM Repair:** 21. Para una discusión más profunda sobre los problemas asociados a la falta de comprensión de Google Translate, véase D. R. Hofstadter, "La superficialidad de Google Translate", The Atlantic, 30 de e...

**Confidence:** 0.3087463676929474

---

### Issue 389 ✅ FIXED

**English:** 22.  D. R. Hofstadter, Gödel, Escher, Bach: an Eternal Golden Braid (New York: Basic Books, 1979), 603.

**Original Spanish:** He aquí otro ejemplo:

**🔍 Vector Search (0.52):** He aquí otro ejemplo:

**✨ LLM Repair:** "D.R. Hofstadter, Gödel, Escher, Bach: una trenza dorada eterna (Nueva York: Basic Books, 1979), 603." ±

**Confidence:** 0.38446909189224243

---

### Issue 390 ✅ FIXED

**English:** 23.  E. Davis and G. Marcus, “Commonsense Reasoning and Commonsense Knowledge in Artificial Intelligence,” Communications of the ACM 58, no. 9 (2015): 92–103.

**Original Spanish:** problema 2: Supongamos que la cadena abc se cambia por abd. ¿Cómo se cambiaría la cadena ppqqrrss según «la misma regla»?

**🔍 Vector Search (0.44):** problema 2: Supongamos que la cadena abc se cambia por abd. ¿Cómo se cambiaría la cadena ppqqrrss según «la misma regla»?

**✨ LLM Repair:** "23. E. Davis y G. Marcus, 'Razonamiento Común y Conocimiento Común en Inteligencia Artificial', Comunicaciones de la ACM 58, número 9 (2015): 92-103." ±

**Confidence:** 0.33046334981918335

---

### Issue 391 ✅ FIXED

**English:** 24.  O. Vinyals et al., “Show and Tell: A Neural Image Caption Generator,” in Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition (2015), 3156–64; A. Karpathy and L. Fei-Fei,...

**Original Spanish:** Incluso en este sencillo micromundo alfabético, la igualdad puede ser bastante sutil, al menos para una máquina. En el problema 2, una aplicación literal de la regla «sustituir la letra más a la derec...

**🔍 Vector Search (0.53):** Incluso en este sencillo micromundo alfabético, la igualdad puede ser bastante sutil, al menos para una máquina. En el problema 2, una aplicación literal de la regla «sustituir la letra más a la derec...

**✨ LLM Repair:** 24. O. Vinyals et al., "Muestra y Cuenta: Un Generador de Captiones de Imágenes Neural", en "Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition" (2015), pp. 3156-64; A. Karp...

**Confidence:** 0.3503186106681824

---

### Issue 392 📏 OVER-LONG (FIXED)

**English:** 25.  Figure 39 is a simplified version of the system described in Vinyals et al., “Show and Tell.”

**Original Spanish:** El problema 2 ilustra, en este micromundo, la noción general de deslizamiento conceptual, una idea f...

**📏 LLM Resized:** Figura 39 es una versión simplificada del sistema descrito en "Show and Tell" de Vinyals et al. ±

**Confidence:** 0.15

---

### Issue 393 ✅ FIXED

**English:** 26.  J. Markoff, “Researchers Announce Advance in Image-Recognition Software,” New York Times, Nov. 17, 2014.

**Original Spanish:** Veamos ahora este problema:

**🔍 Vector Search (0.35):** Veamos ahora este problema:

**✨ LLM Repair:** "26. J. Markoff, 'Investigadores anuncian avances en software de reconocimiento de imágenes', The New York Times, 17 de noviembre de 2014." ±

**Confidence:** 0.22608532011508942

---

### Issue 394 ✅ FIXED

**English:** 28.  A. Linn, “Picture This: Microsoft Research Project Can Interpret, Caption Photos,” AI Blog, May 28, 2015, blogs.microsoft.com/ai/picture-this-microsoft-research-project-can-interpret-caption-phot...

**Original Spanish:** La mayoría de la gente responde «xya», porque se supone que la «sucesora» de z es a. Pero imaginemos un programa informático que no tiene el concepto de abecedario «circular» y para el que, por tanto,...

**🔍 Vector Search (0.51):** La mayoría de la gente responde «xya», porque se supone que la «sucesora» de z es a. Pero imaginemos un programa informático que no tiene el concepto de abecedario «circular» y para el que, por tanto,...

**✨ LLM Repair:** "28 de mayo de 2015. A. Linn, 'Imagina Esto: Proyecto de Investigación de Microsoft Puede Interpretar y Describir Fotos', Blog de AI, blogs.microsoft.com/ai/picture-this-microsoft-research-project-can...

**Confidence:** 0.3263418674468994

---

### Issue 395 ✅ FIXED

**English:** 1.  Transcript from www.chakoteya.net/NextGen/130.htm.

**Original Spanish:** (empty)

**🆕 LLM Generated:** 1. Transcripción de www.chakoteya.net/NextGen/130.htm ±

**Confidence:** 0.05

---

### Issue 396 ✅ FIXED

**English:** 2.  Quoted in F. Manjoo, “Where No Search Engine Has Gone Before,” Slate, April 11, 2013, www.slate.com/articles/technology/technology/2013/04/google_has_a_single_towering_obsession_it_wants_to_build_...

**Original Spanish:** (empty)

**🆕 LLM Generated:** "Citado en F. Manjoo, 'Where No Search Engine Has Gone Before', Slate, 11 de abril de 2013, www.slate.com/articles/technology/technology/2013/04/google_has_a_single_towering_obsession_it_wants_to_buil...

**Confidence:** 0.05

---

### Issue 397 ✅ FIXED

**English:** 3.  Quoted in C. Thompson, “What Is I.B.M.’s Watson?,” New York Times Magazine, June 16, 2010.

**Original Spanish:** (empty)

**🆕 LLM Generated:** "Citado en C. Thompson, '¿Qué es IBM's Watson?', Nueva York Times Magazine, 16 de junio de 2010." ±

**Confidence:** 0.05

---

### Issue 398 ✅ FIXED

**English:** 4.  Quoted in K. Johnson, “How ‘Star Trek’ Inspired Amazon’s Alexa,” Venture Beat, June 7, 2017, venturebeat.com/2017/06/07/how-star-trek-inspired-amazons-alexa.

**Original Spanish:** (empty)

**🆕 LLM Generated:** "4. Citado en K. Johnson, 'Cómo 'Star Trek' inspiró a Amazon Alexa', Venture Beat, 7 de junio de 2017, venturebeat.com/2017/06/07/how-star-trek-inspired-amazons-alexa." ±

**Confidence:** 0.05

---

### Issue 399 ✅ FIXED

**English:** 5.  Wikipedia, s.v. “Watson (computer),” accessed Dec. 16, 2018, en.wikipedia.org/wiki/Watson_(computer).

**Original Spanish:** (empty)

**🆕 LLM Generated:** Wikipedia, s.v. "Watson (ordenador)", consultado el 16 de diciembre de 2018, es.wikipedia.org/wiki/Watson_(ordenador). ±

**Confidence:** 0.05

---

### Issue 400 ✅ FIXED

**English:** 6.  Thompson, “What Is I.B.M.’s Watson?”

**Original Spanish:** (empty)

**🆕 LLM Generated:** "¿Qué es Watson de IBM?" ±

**Confidence:** 0.05

---

### Issue 401 ✅ FIXED

**English:** 7.  A meme made popular on the television show The Simpsons.

**Original Spanish:** (empty)

**🆕 LLM Generated:** 7. Un meme que se hizo popular en el programa de televisión Los Simpson. ±

**Confidence:** 0.05

---

### Issue 402 ✅ FIXED

**English:** 8.  K. Jennings, “The Go Champion, the Grandmaster, and Me,” Slate, March 15, 2016, www.slate.com/articles/technology/technology/2016/03/google_s_alphago_defeated_go_champion_lee_sedol_ken_jennings_ex...

**Original Spanish:** (empty)

**🆕 LLM Generated:** 8. K. Jennings, "El Campeón de Go, el Gran Maestro y Yo", Slate, 15 de marzo de 2016, www.slate.com/articles/technology/technology/2016/03/google_s_alphago_defeated_go_champion_lee_sedol_ken_jennings_...

**Confidence:** 0.05

---

### Issue 403 ✅ FIXED

**English:** 10.  J. C. Dvorak, “Was IBM’s Watson a Publicity Stunt from the Start?,” PC Magazine, Oct. 30, 2013, www.pcmag.com/article2/0,2817,2426521,00.asp.

**Original Spanish:** (empty)

**🆕 LLM Generated:** Diez. J.C. Dvorak, "¿Fue IBM's Watson un Truco de Relaciones Públicas desde el Principio?", PC Magazine, 30 de octubre de 2013, www.pcmag.com/articulo/0,2817,2426521,00.asp. ±

**Confidence:** 0.05

---

### Issue 404 ✅ FIXED

**English:** 11.  M. J. Yuan, “Watson and Healthcare,” IBM Developer website, April 12, 2011, www.ibm.com/developerworks/library/os-ind-watson/index.html.

**Original Spanish:** (empty)

**🆕 LLM Generated:** "11. M. J. Yuan, «Watson y la atención médica», sitio web IBM Developer, 12 de abril de 2011, www.ibm.com/developerworks/library/os-ind-watson/index.html." ±

**Confidence:** 0.05

---

### Issue 405 ✅ FIXED

**English:** 12.  “Artificial Intelligence Positioned to Be a Game-Changer,” 60 Minutes, Oct. 9, 2016, www.cbsnews.com/news/60-minutes-artificial-intelligence-charlie-rose-robot-sophia.

**Original Spanish:** (empty)

**🆕 LLM Generated:** "La inteligencia artificial está posicionada para ser un cambio de juego," 60 Minutos, 9 de octubre de 2016, www.cbsnews.com/noticias/60-minutos-inteligencia-artificial-charlie-rose-robot-sophia. ±

**Confidence:** 0.05

---

### Issue 406 ✅ FIXED

**English:** 14.  P. Rajpurkar et al., “SQuAD: 100,000+ Questions for Machine Comprehension of Text,” in Proceedings of the 2016 Conference on Empirical Methods in Natural Language Processing (2016), 2383–92.

**Original Spanish:** (empty)

**🆕 LLM Generated:** Rajpurkar et al., "SQuAD: más de 100,000 preguntas para la comprensión automática del texto", en Actas de la Conferencia sobre Métodos Empíricos en el Procesamiento del Lenguaje Natural (2016), 2383–9...

**Confidence:** 0.05

---

### Issue 407 ✅ FIXED

**English:** 16.  A. Linn, “Microsoft Creates AI That Can Read a Document and Answer Questions About It as Well as a Person,” AI Blog, Microsoft, Jan. 15, 2018, blogs.microsoft.com/ai/microsoft-creates-ai-can-read...

**Original Spanish:** (empty)

**🆕 LLM Generated:** En enero de 2018, Microsoft creó una inteligencia artificial capaz de leer un documento y responder preguntas sobre él tan bien como lo haría una persona. Esta innovadora tecnología, bautizada como "M...

**Confidence:** 0.05

---

### Issue 408 ✅ FIXED

**English:** 17.  Quoted in “AI Beats Humans at Reading Comprehension for the First Time,” Technology.org, Jan. 17, 2018, www.technology.org/2018/01/17/ai-beats-humans-at-reading-comprehension-for-the-first-time.

**Original Spanish:** (empty)

**🆕 LLM Generated:** "Citado en 'AI supera a los humanos en comprensión de lectura por primera vez', Technology.org, 17 de enero de 2018, www.technology.org/2018/01/17/ai-beats-humans-at-reading-comprehension-for-the-firs...

**Confidence:** 0.05

---

### Issue 409 ✅ FIXED

**English:** 18.  D. Harwell, “AI Models Beat Humans at Reading Comprehension, but They’ve Still Got a Ways to Go,” Washington Post, Jan. 16, 2018.

**Original Spanish:** (empty)

**🆕 LLM Generated:** "18 de enero de 2018. D. Harwell, 'Modelos de IA superan a los humanos en comprensión lectora, pero aún les falta mucho por recorrer', The Washington Post." ±

**Confidence:** 0.05

---

### Issue 410 ✅ FIXED

**English:** 19.  P. Clark et al., “Think You Have Solved Question Answering? Try ARC, the AI2 Reasoning Challenge,” arXiv:1803.05457 (2018).

**Original Spanish:** (empty)

**🆕 LLM Generated:** 19. P. Clark et al., "¿Crees que has resuelto el desafío de respuesta a preguntas? Prueba ARC, el Desafío de Razonamiento de AI2", arXiv:1803.05457 (2018). ±

**Confidence:** 0.05

---

### Issue 411 ✅ FIXED

**English:** 21.  ARC Dataset Leaderboard, Allen Institute for Artificial Intelligence, accessed Dec. 17, 2018, leaderboard.allenai.org/arc/submissions/public.

**Original Spanish:** (empty)

**🆕 LLM Generated:** 21. Ranking de datos del conjunto ARC, Instituto de Inteligencia Artificial Allen, consultado el 17 de diciembre de 2018, leaderboard.allenai.org/arc/submissions/public. ±

**Confidence:** 0.05

---

### Issue 412 ✅ FIXED

**English:** 22.  All of the examples in this section are from E. Davis, L. Morgenstern, and C. Ortiz, “The Winograd Schema Challenge,” accessed Dec. 17, 2018, cs.nyu.edu/faculty/davise/papers/WS.html.

**Original Spanish:** Parte V. La barrera del significado

**🔍 Vector Search (0.34):** Parte V. La barrera del significado

**✨ LLM Repair:** "Todos los ejemplos de esta sección son del E. Davis, L. Morgenstern y C. Ortiz, 'El desafío del esquema de Winograd', accedido el 17 de diciembre de 2018, cs.nyu.edu/faculty/davise/papers/WS.html." ±

**Confidence:** 0.29647380113601685

---

### Issue 413 ✅ FIXED

**English:** 23.  T. Winograd, Understanding Natural Language (New York: Academic Press, 1972).

**Original Spanish:** (empty)

**🆕 LLM Generated:** 23. T. Winograd, Entendiendo el Lenguaje Natural (Nueva York: Editorial Académica, 1972). ±

**Confidence:** 0.05

---

### Issue 414 ✅ FIXED

**English:** 24.  H. J. Levesque, E. Davis, and L. Morgenstern, “The Winograd Schema Challenge,” in AAAI Spring Symposium: Logical Formalizations of Commonsense Reasoning (American Association for Artificial Intel...

**Original Spanish:** (empty)

**🆕 LLM Generated:** 24. H.J. Levesque, E. Davis y L. Morgenstern, "El Desafío del Esquema de Winograd", en el AAAI Spring Symposium: Formalizaciones Lógicas de la Razonamiento Común (Asociación Estadounidense para la Int...

**Confidence:** 0.05

---

### Issue 415 ✅ FIXED

**English:** 25.  T. H. Trinh and Q. V. Le, “A Simple Method for Commonsense Reasoning,” arXiv:1806.02847 (2018).

**Original Spanish:** (empty)

**🆕 LLM Generated:** "25. T.H. Trinh y Q.V. Le, “Un método simple para la razonamiento común”, arXiv:1806.02847 (2018)." ±

**Confidence:** 0.05

---

### Issue 416 ✅ FIXED

**English:** 26.  Quoted in K. Bailey, “Conversational AI and the Road Ahead,” Tech Crunch, Feb. 25, 2017, techcrunch.com/2017/02/25/conversational-ai-and-the-road-ahead.

**Original Spanish:** (empty)

**🆕 LLM Generated:** "26. Citado en K. Bailey, “Inteligencia artificial conversacional y el camino por delante”, Tech Crunch, 25 de febrero de 2017, techcrunch.com/2017/02/25/conversational-ai-and-the-road-ahead." ±

**Confidence:** 0.05

---

### Issue 417 ✅ FIXED

**English:** 27.  H. Chen et al., “Attacking Visual Language Grounding with Adversarial Examples: A Case Study on Neural Image Captioning,” in Proceedings of the 56th Annual Meeting of the Association for Computat...

**Original Spanish:** (empty)

**🆕 LLM Generated:** "Chen H., et al., “Atacar el anclaje del lenguaje visual con ejemplos adversos: un estudio de caso sobre la captación de imágenes neuronales”, en las Actas de la 56ª Reunión Anual de la Asociación par...

**Confidence:** 0.05

---

### Issue 418 ✅ FIXED

**English:** 28.  N. Carlini and D. Wagner, “Audio Adversarial Examples: Targeted Attacks on Speech-to-Text,” in Proceedings of the First Deep Learning and Security Workshop (2018).

**Original Spanish:** (empty)

**🆕 LLM Generated:** "28. N. Carlini y D. Wagner, 'Ejemplos adversariales de audio: ataques dirigidos en Speech-to-Text', en Actas del Primer Taller de Aprendizaje Profundo y Seguridad (2018)." ±

**Confidence:** 0.05

---

### Issue 419 ✅ FIXED

**English:** 29.  R. Jia and P. Liang, “Adversarial Examples for Evaluating Reading Comprehension Systems,” in Proceedings of the 2017 Conference on Empirical Methods in Natural Language Processing (2017).

**Original Spanish:** (empty)

**🆕 LLM Generated:** 29. R. Jia y P. Liang, "Ejemplos adversariales para evaluar sistemas de comprensión lectora", en las Actas de la Conferencia sobre Métodos Empíricos en el Procesamiento del Lenguaje Natural (2017). ±

**Confidence:** 0.05

---

### Issue 420 ✅ FIXED

**English:** 30.	C. D. Manning, “Last Words: Computational Linguistics and Deep Learning,” Nautilus, April 2017.

**Original Spanish:** (empty)

**🆕 LLM Generated:** "30. C. D. Manning, 'Últimas palabras: Lingüística computacional y aprendizaje profundo', Nautilus, abril de 2017." ±

**Confidence:** 0.05

---

### Issue 421 📏 OVER-LONG (FIXED)

**English:** 1.  G.-C. Rota, “In Memoriam of Stan Ulam: The Barrier of Meaning,” Physica D Nonlinear Phenomena 22 (1986): 1–3.

**Original Spanish:** Si vamos más allá, solemos conceptualizar las relaciones sociales en términos de temperatura física....

**📏 LLM Resized:** "1. G.-C. Rota, 'En memoria de Stan Ulam: La barrera del significado', Física D Fenómenos no lineales 22 (1986): 1-3." ±

**Confidence:** 0.15

---

### Issue 422 ✅ FIXED

**English:** 7.  L. W. Barsalou, “Grounded Cognition,” Annual Review of Psychology 59 (2008): 617–45.

**Original Spanish:** Tres meses: S. puede distinguir entre expresiones faciales que representan felicidad y tristeza y las generaliza entre las diversas personas con las que se relaciona. Ha abstraído los conceptos de car...

**🔍 Vector Search (0.42):** Tres meses: S. puede distinguir entre expresiones faciales que representan felicidad y tristeza y las generaliza entre las diversas personas con las que se relaciona. Ha abstraído los conceptos de car...

**✨ LLM Repair:** 7. L.W. Barsalou, "Cognición basada en la realidad", Anuario de Psicología 59 (2008): 617-45. ±

**Confidence:** 0.3621729910373688

---

### Issue 423 ✅ FIXED

**English:** 8.  L. W. Barsalou, “Situated Simulation in the Human Conceptual System,” Language and Cognitive Processes 18, no. 5–6 (2003): 513–62.

**Original Spanish:** Seis meses: S. ya reconoce cuándo la gente le está diciendo «adiós con la mano» y puede hacer lo mismo. Ha abstraído el concepto visual de saludar con la mano y ha aprendido a responder con el «mismo»...

**🔍 Vector Search (0.47):** Seis meses: S. ya reconoce cuándo la gente le está diciendo «adiós con la mano» y puede hacer lo mismo. Ha abstraído el concepto visual de saludar con la mano y ha aprendido a responder con el «mismo»...

**✨ LLM Repair:** 8. L.W. Barsalou, "Simulación situada en el sistema conceptual humano", Lenguaje y Procesos Cognitivos 18, núms. 5-6 (2003): 513-62. ±

**Confidence:** 0.41885095834732056

---

### Issue 424 📏 OVER-LONG (FIXED)

**English:** 10.  G. Lakoff and M. Johnson, Metaphors We Live By (Chicago: University of Chicago Press, 1980).

**Original Spanish:** Tres años: S. reconoce letras sueltas del abecedario escritas por diferentes personas e impresas. Es...

**📏 LLM Resized:** Diez. G. Lakoff y M. Johnson, Las metáforas en las que vivimos (Chicago: Universidad de Chicago Press, 1980). ±

**Confidence:** 0.15

---

### Issue 425 📏 OVER-LONG (FIXED)

**English:** 11.  L. E. Williams and J. A. Bargh, “Experiencing Physical Warmth Promotes Interpersonal Warmth,” Science 322, no. 5901 (2008): 606–607.

**Original Spanish:** Ocho años: He oído por casualidad a J., la mejor amiga de S., contándole a S. que su madre se había ...

**📏 LLM Resized:** 11. L.E. Williams y J.A. Bargh, "Experimentar calor físico promueve la calidez interpersonal", Ciencia 322, no. 5901 (2008): 606-607. ±

**Confidence:** 0.15

---

### Issue 426 ✅ FIXED

**English:** 12.  C. B. Zhong and G. J. Leonardelli, “Cold and Lonely: Does Social Exclusion Literally Feel Cold?,” Psychological Science 19, no. 9 (2008): 838–42.

**Original Spanish:** Trece años: S. empieza a ser una adolescente rebelde. Le he pedido muchas veces que limpie su habitación. Hoy me ha gritado: «No puedes obligarme; ¡Abraham Lincoln liberó a los esclavos!». Me he enfad...

**🔍 Vector Search (0.55):** Trece años: S. empieza a ser una adolescente rebelde. Le he pedido muchas veces que limpie su habitación. Hoy me ha gritado: «No puedes obligarme; ¡Abraham Lincoln liberó a los esclavos!». Me he enfad...

**✨ LLM Repair:** "12. C.B. Zhong y G.J. Leonardelli, 'Frío y Solo: ¿La exclusión social literalmente produce una sensación de frío?', Ciencia Psicológica 19, no. 9 (2008): 838-42." ±

**Confidence:** 0.26370662450790405

---

### Issue 427 ✅ FIXED

**English:** 13.  D. R. Hofstadter, I Am a Strange Loop (New York: Basic Books, 2007). The quotation is from the front book flap. My description also echoes ideas proposed by the philosopher Daniel Dennett in his ...

**Original Spanish:** Dieciséis años: El interés de S. por la música va en aumento. A los dos nos gusta jugar en el coche a poner una emisora de música clásica a mitad de una pieza y ver quién de los dos puede averiguar an...

**🔍 Vector Search (0.55):** Dieciséis años: El interés de S. por la música va en aumento. A los dos nos gusta jugar en el coche a poner una emisora de música clásica a mitad de una pieza y ver quién de los dos puede averiguar an...

**✨ LLM Repair:** 13. D.R. Hofstadter, Soy un bucle extraño (Nueva York: Basic Books, 2007). La cita es del reverso de la sobrecubierta del libro. Mi descripción también refleja ideas propuestas por el filósofo Daniel ...

**Confidence:** 0.3660241961479187

---

### Issue 428 📏 OVER-LONG (FIXED)

**English:** 15.  I borrowed this argument from an actual legal case. See “Blogs as Graffiti? Using Analogy and Metaphor in Case Law,” IdeaBlawg, March 17, 2012, www.ideablawg.ca/blog/2012/3/17/blogs-as-graffiti-u...

**Original Spanish:** Veintiséis años: S. se ha licenciado en Derecho y la han contratado en un prestigioso bufete. Su cli...

**📏 LLM Resized:** 15. Este argumento lo tomé prestado de un caso legal real. Consulte "Los blogs como graffiti? El uso de analogía y metáfora en el derecho", IdeaBlawg, 17 de marzo de 2012, www.ideablawg.ca/blog/2012/3...

**Confidence:** 0.15

---

### Issue 429 📏 OVER-LONG (FIXED)

**English:** 17.  Hofstadter and Sander, Surfaces and Essences, 3.

**Original Spanish:** En resumen, las analogías, casi siempre inconscientes, son la base de nuestra capacidad de abstraer ...

**📏 LLM Resized:** Diecisiete. Hofstadter y Sander, Superficies y Esencias, tres. ±

**Confidence:** 0.15

---

### Issue 430 📏 OVER-LONG (FIXED)

**English:** 18.  M. Minsky, “Decentralized Minds,” Behavioral and Brain Sciences 3, no. 3 (1980): 439–40.

**Original Spanish:** En este capítulo he esbozado algunas ideas procedentes de trabajos recientes de psicología sobre los...

**📏 LLM Resized:** 18. M. Minsky, "Mentes Descentralizadas", Ciencias del Comportamiento y Cerebro 3, n.º 3 (1980): 439-40. ±

**Confidence:** 0.15

---

### Issue 431 ✅ FIXED

**English:** 15: Knowledge, Abstraction, and Analogy in Artificial Intelligence

**Original Spanish:** 14. Sobre la comprensión

**🔍 Vector Search (0.88):** 15. Conocimiento, abstracción y analogía en la inteligencia artificial

**Confidence:** 0.44556528329849243

---

### Issue 432 ✅ FIXED

**English:** 1.  D. B. Lenat and J. S. Brown, “Why AM and EURISKO Appear to Work,” Artificial Intelligence 23, no. 3 (1984): 269–94.

**Original Spanish:** 15. Conocimiento, abstracción y analogía en la inteligencia artificial

**🔍 Vector Search (0.42):** 15. Conocimiento, abstracción y analogía en la inteligencia artificial

**✨ LLM Repair:** "1. D.B. Lenat y J.S. Brown, '¿Por qué AM y EURISKO parecen funcionar', Inteligencia Artificial 23, nº 3 (1984): 269-94." ±

**Confidence:** 0.3992961645126343

---

### Issue 433 ✅ FIXED

**English:** 2.  These examples are from C. Metz, “One Genius’ Lonely Crusade to Teach a Computer Common Sense,” Wired, March 24, 2016, www.wired.com/2016/03/doug-lenat-artificial-intelligence-common-sense-engine,...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Estos ejemplos son de C. Metz, "La solitaria cruzada de un genio para enseñarle a una computadora sentido común", Wired, 24 de marzo de 2016, www.wired.com/2016/03/doug-lenat-artificial-intelligence-c...

**Confidence:** 0.05

---

### Issue 434 ✅ FIXED

**English:** 3.  Lenat notes that the company is increasingly able to automate the process of obtaining new assertions (presumably by mining the web). From D. Lenat, “50 Shades of Symbolic Representation and Reaso...

**Original Spanish:** (empty)

**🆕 LLM Generated:** 3. Lenat observó que la empresa está cada vez más en condiciones de automatizar el proceso de obtener nuevas afirmaciones (presuntamente mediante la minería web). De D. Lenat, “50 tonos de representac...

**Confidence:** 0.05

---

### Issue 435 ✅ FIXED

**English:** 5.  A detailed, nontechnical description of the Cyc project is given in chapter 4 of H. R. Ekbia, Artificial Dreams: The Quest for Non-biological Intelligence (Cambridge, U.K.: Cambridge University Pr...

**Original Spanish:** (empty)

**🆕 LLM Generated:** En el Capítulo 4 de H. R. Ekbia, "Sueños Artificiales: La Búsqueda de la Inteligencia No Biológica" (Cambridge, Reino Unido: Cambridge University Press, 2008), se ofrece una descripción detallada y no...

**Confidence:** 0.05

---

### Issue 436 ✅ FIXED

**English:** 6.  Lucid company’s webpage: lucid.ai.

**Original Spanish:** (empty)

**🆕 LLM Generated:** 6. Página web de la compañía Lucid: lucid.ai ±

**Confidence:** 0.05

---

### Issue 437 ✅ FIXED

**English:** 7.  P. Domingos, The Master Algorithm (New York: Basic Books, 2015), 35.

**Original Spanish:** (empty)

**🆕 LLM Generated:** "Capítulo 7. P. Domingos, 'El algoritmo maestro' (Nueva York: Basic Books, 2015), 35." ±

**Confidence:** 0.05

---

### Issue 438 ✅ FIXED

**English:** 8.  From “The Myth of AI: A Conversation with Jaron Lanier,” Edge, Nov. 14, 2014, www.edge.org/conversation/jaron_lanier-the-myth-of-ai.

**Original Spanish:** (empty)

**🆕 LLM Generated:** 8. De "El Mito de la IA: Una Conversación con Jaron Lanier", Edge, 14 de noviembre de 2014, www.edge.org/conversation/jaron_lanier-the-myth-of-ai. ±

**Confidence:** 0.05

---

### Issue 439 ✅ FIXED

**English:** 9.  For example, see N. Watters et al., “Visual Interaction Networks,” Advances in Neural Information Processing Systems 30 (2017): 4539–47; T. D. Ullman et al., “Mind Games: Game Engines as an Archit...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Para ilustrar, véase N. Watters et al., "Redes de interacción visual", Avances en procesamiento de información neuronal 30 (2017): 4539-47; T.D. Ullman et al., “Juegos mentales: motores de juegos como...

**Confidence:** 0.05

---

### Issue 440 ✅ FIXED

**English:** 10.  J. Pearl, “Theoretical Impediments to Machine Learning with Seven Sparks from the Causal Revolution,” in Proceedings of the Eleventh ACM International Conference on Web Search and Data Mining (20...

**Original Spanish:** (empty)

**🆕 LLM Generated:** 10. J. Pearl, "Impedimentos teóricos para el aprendizaje automático con siete chispas de la revolución causal", en Actas de la Undécima Conferencia Internacional ACM sobre Búsqueda Web y Minería de Da...

**Confidence:** 0.05

---

### Issue 441 ✅ FIXED

**English:** 11.  For an insightful discussion on what is missing in deep learning, see G. Marcus, “Deep Learning: A Critical Appraisal,” arXiv:1801.00631 (2018).

**Original Spanish:** (empty)

**🆕 LLM Generated:** Para una discusión ilustrativa sobre qué falta en el aprendizaje profundo, véase G. Marcus, "Evaluación Crítica del Aprendizaje Profundo", arXiv:1801.00631 (2018). ±

**Confidence:** 0.05

---

### Issue 442 ✅ FIXED

**English:** 12.  DARPA Fiscal Year 2019 Budget Estimates, Feb. 2018, accessed Dec. 18, 2018, www.darpa.mil/attachments/DARPAFY19PresidentsBudgetRequest.pdf.

**Original Spanish:** (empty)

**🆕 LLM Generated:** No translation provided for this English text as it is not literary in nature and does not have a tone or style that can be maintained in Spanish. It is a reference to a specific government document. ...

**Confidence:** 0.05

---

### Issue 443 ✅ FIXED

**English:** 13.  English version: M. Bongard, Pattern Recognition (New York: Spartan Books, 1970).

**Original Spanish:** (empty)

**🆕 LLM Generated:** 13. Versión en inglés: M. Bongard, Reconocimiento de patrones (Nueva York: Editorial Espartano, 1970). ±

**Confidence:** 0.05

---

### Issue 444 ✅ FIXED

**English:** 14.  All of the Bongard-problem images I give here are from Harry Foundalis’s Index of Bongard Problems website, www.foundalis.com/res/bps/bpidx.htm, which gives Bongard’s one hundred problems as well...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Todos los imágenes de problemas de Bongard que proporciono aquí son del sitio web del índice de problemas de Bongard de Harry Foundalis, www.foundalis.com/res/bps/bpidx.htm, donde se presentan los cie...

**Confidence:** 0.05

---

### Issue 445 ✅ FIXED

**English:** 15.  R. M. French, The Subtlety of Sameness (Cambridge, Mass.: MIT Press, 1995).

**Original Spanish:** (empty)

**🆕 LLM Generated:** "R. M. French, La sutileza de la similitud (Cambridge, Mass.: MIT Press, 1995)." ±

**Confidence:** 0.05

---

### Issue 446 ✅ FIXED

**English:** 16.  One particularly interesting program that attempted to solve Bongard problems was created by Harry Foundalis when he was a graduate student in Douglas Hofstadter’s research group at Indiana Unive...

**Original Spanish:** (empty)

**🆕 LLM Generated:** 16. En particular, un programa muy interesante que intentó resolver los problemas de Bongard fue creado por Harry Foundalis cuando era estudiante de posgrado en el grupo de investigación de Douglas Ho...

**Confidence:** 0.05

---

### Issue 447 ✅ FIXED

**English:** 17.  S. Stabinger, A. Rodríguez-Sánchez, and J. Piater, “25 Years of CNNs: Can We Compare to Human Abstraction Capabilities?,” in Proceedings of the International Conference on Artificial Neural Netwo...

**Original Spanish:** (empty)

**🆕 LLM Generated:** 17. S. Stabinger, A. Rodríguez-Sánchez y J. Piater, “25 años de CNN: ¿Podemos comparar con las habilidades humanas de abstracción?” en Actas de la Conferencia Internacional sobre Redes Neuronales Arti...

**Confidence:** 0.05

---

### Issue 448 ✅ FIXED

**English:** 18.  When I say “most people,” I am referring to the results of surveys I gave to people as part of my dissertation work. See M. Mitchell, Analogy-Making as Perception (Cambridge, Mass.: MIT Press, 19...

**Original Spanish:** (empty)

**🆕 LLM Generated:** 18. Cuando digo "la mayoría de las personas", me refiero a los resultados de las encuestas que distribuí entre la gente como parte de mi trabajo para mi tesis. Ver M. Mitchell, La percepción como Anal...

**Confidence:** 0.05

---

### Issue 449 ✅ FIXED

**English:** 19.  Hofstadter coined the term conceptual slippage in his discussion of Bongard problems in chapter 19 of D. R. Hofstadter, Gödel, Escher, Bach: an Eternal Golden Braid (New York: Basic Books, 1979).

**Original Spanish:** (empty)

**🆕 LLM Generated:** En el capítulo 19 de "Gödel, Escher, Bach", Hofstadter acuñó el término deslizamiento conceptual en su análisis sobre los problemas de Bongard. ±

**Confidence:** 0.05

---

### Issue 450 ✅ FIXED

**English:** 21.  A detailed description of Copycat is given in chapter 5 of D. R. Hofstadter and the Fluid Analogies Research Group, Fluid Concepts and Creative Analogies: Computer Models of the Fundamental Mecha...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Capítulo 5 de "Fluid Concepts and Creative Analogies", de D. R. Hofstadter y el Grupo de Investigación de Analogías Fluides (Nueva York: Basic Books, 1995), ofrece una descripción detallada de Copycat...

**Confidence:** 0.05

---

### Issue 451 ✅ FIXED

**English:** 22.  J. Marshall, “A Self-Watching Model of Analogy-Making and Perception,” Journal of Experimental and Theoretical Artificial Intelligence 18, no. 3 (2006): 267–307.

**Original Spanish:** (empty)

**🆕 LLM Generated:** "22. J. Marshall, "Un modelo autobservador de la formación de analogías y percepción", Revista de Inteligencia Artificial Experimental y Teórica 18, n.º 3 (2006): 267-307." ±

**Confidence:** 0.05

---

### Issue 452 ✅ FIXED

**English:** 23.  Several of these programs are described in Hofstadter and the Fluid Analogies Research Group, Fluid Concepts and Creative Analogies.

**Original Spanish:** (empty)

**🆕 LLM Generated:** En varios de estos programas se describe en Hofstadter y el Grupo de Investigación de Analogías Fluides, Concepciones y Analogías Creativas. ±

**Confidence:** 0.05

---

### Issue 453 ✅ FIXED

**English:** 24.  A. Karpathy, “The State of Computer Vision and AI: We Are Really, Really Far Away,” Andrej Karpathy blog, Oct. 22, 2012, karpathy.github.io/2012/10/22/state -of-computer-vision.

**Original Spanish:** (empty)

**🆕 LLM Generated:** 24. A. Karpathy, “El Estado de la Visión por Computadora y la IA: Estamos Realmente, Realmente Lejanos”, Blog de Andrej Karpathy, 22 de octubre de 2012, karpathy.github.io/2012/10/22/estado-de-la-visi...

**Confidence:** 0.05

---

### Issue 454 ✅ FIXED

**English:** 25.  See Stanford Encyclopedia of Philosophy, s.v. “Dualism,” plato.stanford.edu/entries/dualism/.

**Original Spanish:** 16. Preguntas, respuestas y especulaciones

**🔍 Vector Search (0.43):** 16. Preguntas, respuestas y especulaciones

**✨ LLM Repair:** No se ha proporcionado texto en español para traducir del inglés. Por favor, proporcione el texto en español correspondiente para realizar la traducción. ±

**Confidence:** 0.3105963468551636

---

### Issue 455 ✅ FIXED

**English:** 26.  For a cogent philosophical discussion of the embodiment hypothesis in cognitive science, see A. Clark, Being There: Putting Brain, Body, and World Together Again (Cambridge, Mass.: MIT Press, 199...

**Original Spanish:** Agradecimientos

**🔍 Vector Search (0.48):** Agradecimientos

**✨ LLM Repair:** Para una discusión filosófica clara y coherente de la hipótesis de la encarnación en la ciencia cognitiva, consulte A. Clark, Ser allí: Volver a unir cerebro, cuerpo y mundo (Cambridge, Mass.: Editori...

**Confidence:** 0.06700709462165833

---

### Issue 456 📏 OVER-LONG (FIXED)

**English:** 16: Questions, Answers, and Speculations

**Original Spanish:** En una entrada del blog de la web de su empresa, el presidente y director jurídico de Microsoft, Bra...

**📏 LLM Resized:** 16: Preguntas, Respuestas y Especulaciones ±

**Confidence:** 0.15

---

### Issue 457 ✅ FIXED

**English:** 1.  “Automated Vehicles for Safety,” National Highway Traffic Safety Administration website, www.nhtsa.gov/technology-innovation/automated-vehicles-safety#issue-road-self-driving.

**Original Spanish:** La tecnología de reconocimiento facial plantea dudas que afectan directamente a la protección de derechos humanos fundamentales como la privacidad y la libertad de expresión. Estas cuestiones aumentan...

**🔍 Vector Search (0.46):** La tecnología de reconocimiento facial plantea dudas que afectan directamente a la protección de derechos humanos fundamentales como la privacidad y la libertad de expresión. Estas cuestiones aumentan...

**✨ LLM Repair:** "Vehículos Automáticos para la Seguridad", Administración Nacional de Seguridad del Tráfico en Carreteras, sitio web www.nhtsa.gov/tecnología-innovación/vehículos-automáticos-seguridad ±

**Confidence:** 0.4226572513580322

---

### Issue 458 📏 OVER-LONG (FIXED)

**English:** 2.  “Vehicle Cybersecurity: DOT and Industry Have Efforts Under Way, but DOT Needs to Define Its Role in Responding to a Real-World Attack,” General Accounting Office, March 2016, accessed Dec. 18, 20...

**Original Spanish:** Google siguió su ejemplo y anunció que no ofrecería servicios de reconocimiento facial en general a ...

**📏 LLM Resized:** "No hay traducción directa para este texto ya que es una fuente de información específica que contiene detalles técnicos y nombres propios que no tienen un equivalente directo en español. Sin embargo,...

**Confidence:** 0.15

---

### Issue 459 ✅ FIXED

**English:** 5.  “Artificial Intelligence, Automation, and the Economy,” Executive Office of the President, Dec. 2016, www.whitehouse.gov/sites/whitehouse.gov/files/images/EMBARGOED%20AI%20Economy%20Report.pdf.

**Original Spanish:** Esta infraestructura está empezando a formarse. En Estados Unidos, los Gobiernos estatales están empezando a estudiar la creación de normativas, entre ellas sobre el reconocimiento facial y los vehícu...

**🔍 Vector Search (0.40):** Esta infraestructura está empezando a formarse. En Estados Unidos, los Gobiernos estatales están empezando a estudiar la creación de normativas, entre ellas sobre el reconocimiento facial y los vehícu...

**✨ LLM Repair:** "Inteligencia Artificial, Automatización y la Economía", Oficina Ejecutiva de la Presidencia, diciembre de 2016, www.whitehouse.gov/sites/whitehouse.gov/files/images/EMBARGOED%20AI%20Economy%20Report....

**Confidence:** 0.3296782374382019

---

### Issue 460 ✅ FIXED

**English:** 6.  This harks back to what Alan Turing called “Lady Lovelace’s objection,” named for Lady Ada Lovelace, a British mathematician and writer who worked with Charles Babbage on developing the Analytical...

**Original Spanish:** Para llenar este vacío han surgido varios grupos de reflexión sin ánimo de lucro, con frecuencia financiados por ricos empresarios tecnológicos preocupados por la IA. Estas organizaciones —con nombres...

**🔍 Vector Search (0.60):** Para llenar este vacío han surgido varios grupos de reflexión sin ánimo de lucro, con frecuencia financiados por ricos empresarios tecnológicos preocupados por la IA. Estas organizaciones —con nombres...

**✨ LLM Repair:** Este hecho nos remonta a lo que Alan Turing denominó "la objeción de Lady Lovelace", en honor a Ada Lovelace, matemática y escritora británica que trabajó con Charles Babbage en el desarrollo de la Má...

**Confidence:** 0.41711822152137756

---

### Issue 461 ✅ FIXED

**English:** 8.  D. Cope, Virtual Music: Computer Synthesis of Musical Style (Cambridge, Mass.: MIT Press, 2004).

**Original Spanish:** Máquinas morales

**🔍 Vector Search (0.41):** Máquinas morales

**✨ LLM Repair:** 8. D. Cope, Música Virtual: Síntesis por Computadora de Estilo Musical (Cambridge, MA: Editorial del Instituto Tecnológico de Massachusetts, 2004). ±

**Confidence:** 0.24713711440563202

---

### Issue 462 📏 OVER-LONG (FIXED)

**English:** 9.  Quoted in G. Johnson, “Undiscovered Bach? No, a Computer Wrote It,” New York Times, Nov. 11, 1997.

**Original Spanish:** Hasta ahora, mi análisis se ha centrado en las dudas éticas sobre cómo utilizan los humanos la IA. P...

**📏 LLM Resized:** 9. Citado en G. Johnson, "¿Bach sin descubrir? No, un ordenador lo escribió", The New York Times, 11 de noviembre de 1997. ±

**Confidence:** 0.15

---

### Issue 463 ✅ FIXED

**English:** 11.  J. Gottschall, “The Rise of Storytelling Machines,” in What to Think About Machines That Think, ed. J. Brockman (New York: Harper Perennial, 2015), 179–80.

**Original Spanish:** 1. Un robot no puede dañar a un ser humano ni, por inacción, permitir que un ser humano sufra daños.

**🔍 Vector Search (0.49):** 1. Un robot no puede dañar a un ser humano ni, por inacción, permitir que un ser humano sufra daños.

**✨ LLM Repair:** 11. J. Gottschall, "La Ascensión de las Máquinas Narradoras", en ¿Qué Pensar Sobre las Máquinas que Piensan?, editado por J. Brockman (Nueva York: Harper Perennial, 2015), 179-80. ±

**Confidence:** 0.36489564180374146

---

### Issue 464 ✅ FIXED

**English:** 13.  A. Karpathy, “The State of Computer Vision and AI: We Are Really, Really Far Away,” Andrej Karpathy blog, Oct. 22, 2012, karpathy.github.io/2012/10/22/state-of-computer-vision.

**Original Spanish:** 3. Un robot debe proteger su propia existencia siempre que dicha protección no entre en conflicto con la Primera o la Segunda Ley.[167]

**🔍 Vector Search (0.48):** 3. Un robot debe proteger su propia existencia siempre que dicha protección no entre en conflicto con la Primera o la Segunda Ley.[167]

**✨ LLM Repair:** 13. A. Karpatky, "El Estado de la Visión por Computadora y la IA: Estamos Realmente, Realmente Lejos", Blog de Andrej Karpaty, 22 de octubre de 2012, karpaty.github.io/2012/10/22/estado-de-la-vision-p...

**Confidence:** 0.3311346769332886

---

### Issue 465 📏 OVER-LONG (FIXED)

**English:** 14.  C. L. Evans, Broad Band: The Untold Story of the Women Who Made the Internet (New York: Portfolio/Penguin, 2018), 24.

**Original Spanish:** Estas leyes son famosas, pero, en realidad, el propósito de Asimov era demostrar que una serie de re...

**📏 LLM Resized:** CAPÍTULO 14. C. L. Evans, "Ancho de Banda": La historia no contada de las mujeres que construyeron internet (Nueva York: Portfolio / Penguin, 2018), 24. ±

**Confidence:** 0.15

---

### Issue 466 📏 OVER-LONG (FIXED)

**English:** 15.  M. Campbell-Kelly et al., Computer: A History of the Information Machine, 3rd ed. (New York: Routledge, 2018), 80.

**Original Spanish:** El escritor de ciencia ficción Arthur C. Clarke utilizó un recurso argumental similar en su libro de...

**📏 LLM Resized:** 15. M. Campbell-Kelly et al., Computadora: Una historia de la máquina informática, 3.ª edición (Nueva York: Routledge, 2018), 80. ±

**Confidence:** 0.15

---

### Issue 467 ✅ FIXED

**English:** 16.  Quoted in K. Anderson, “Enthusiasts and Skeptics Debate Artificial Intelligence,” Vanity Fair, Nov. 26, 2014.

**Original Spanish:** El comentario de Wiener capta lo que se denomina el problema de la alineación de valores en la IA: la necesidad de que los programadores de IA puedan garantizar que los valores de sus sistemas coincid...

**🔍 Vector Search (0.41):** El comentario de Wiener capta lo que se denomina el problema de la alineación de valores en la IA: la necesidad de que los programadores de IA puedan garantizar que los valores de sus sistemas coincid...

**✨ LLM Repair:** No se encontró una traducción adecuada para este texto ya que no es un fragmento de un libro literario ni contiene diálogo o narrativa que pueda ser traducido al español con un estilo literario. Sin e...

**Confidence:** 0.3414391875267029

---

### Issue 468 📏 OVER-LONG (FIXED)

**English:** 18.  N. Bostrom, “How Long Before Superintelligence?,” International Journal of Future Studies 2 (1998).

**Original Spanish:** El dilema del tranvía es un elemento omnipresente en los cursos universitarios de ética desde hace u...

**📏 LLM Resized:** "18. N. Bostrom, '¿Cuánto tiempo antes de la superinteligencia?', International Journal of Future Studies 2 (1998)." ±

**Confidence:** 0.15

---

### Issue 469 📏 OVER-LONG (FIXED)

**English:** 19.  D. R. Hofstadter, Gödel, Escher, Bach: an Eternal Golden Braid (New York: Basic Books, 1979), 677–78.

**Original Spanish:** El dilema del tranvía ha reaparecido en los últimos tiempos dentro de las informaciones mediáticas s...

**📏 LLM Resized:** 19. D.R. Hofstadter, "Gödel, Escher, Bach: una trenza dorada eterna" (Nueva York: Basic Books, 1979), pp. 677-78. ±

**Confidence:** 0.15

---

### Issue 470 📏 OVER-LONG (FIXED)

**English:** 21.  P. Domingos, The Master Algorithm (New York: Basic Books, 2015), 285–86.

**Original Spanish:** Algunos investigadores de la ética de la IA han sugerido que dejemos de intentar programar directame...

**📏 LLM Resized:** "21. P. Domingos, 'El algoritmo maestro' (Nueva York: Basic Books, 2015), pp. 285-86." ±

**Confidence:** 0.15

---

### Issue 471 📏 OVER-LONG (FIXED)

**English:** 23.  R. Brooks, “The Origins of ‘Artificial Intelligence,’” Rodney Brooks’s blog, April 27, 2018, rodneybrooks.com/forai-the-origins-of-artificial-intelligence.

**Original Spanish:** Hasta ahora hemos visto que las redes neuronales profundas, entrenadas con enormes conjuntos de dato...

**📏 LLM Resized:** "23. R. Brooks, 'Los Orígenes de la 'Inteligencia Artificial',' Blog de Rodney Brooks, 27 de abril de 2018, rodneybrooks.com/forai-los-origenes-de-la-inteligencia-artificial." ±

**Confidence:** 0.15

---

### Issue 472 ✅ FIXED

**English:** The index that appeared in the print version of this title does not match the pages in your e-book. Please use the search function on your e-reading device to search for terms of interest. For your re...

**Original Spanish:** El deslizamiento conceptual también tenía un papel crucial en las diferentes abstracciones que la hija imaginaria S. (del capítulo anterior) hacía a lo largo de los años; por ejemplo, en su analogía j...

**🔍 Vector Search (0.31):** El deslizamiento conceptual también tenía un papel crucial en las diferentes abstracciones que la hija imaginaria S. (del capítulo anterior) hacía a lo largo de los años; por ejemplo, en su analogía j...

**✨ LLM Repair:** El índice que aparece en la edición impresa de este título no coincide con las páginas de su libro electrónico. Por favor utilice la función de búsqueda de su dispositivo de lectura electrónica para b...

**Confidence:** 0.24115636944770813

---

### Issue 473 ✅ FIXED

**English:** abstraction; in Bongard problems; in convolutional neural networks; in human cognition; in letter-string analogy problems

**Original Spanish:** Copycat no era ni un programa simbólico basado en reglas ni una red neuronal, aunque incluía aspectos de la IA simbólica y de la subsimbólica.

**🔍 Vector Search (0.45):** Copycat no era ni un programa simbólico basado en reglas ni una red neuronal, aunque incluía aspectos de la IA simbólica y de la subsimbólica.

**✨ LLM Repair:** Abstracto; en problemas de Bongard; en redes neuronales convolucionales; en la cognición humana; en problemas de analogía de cadenas de letras ±

**Confidence:** 0.29119664430618286

---

### Issue 474 ✅ FIXED

**English:** activations: in encoder-decoder systems; formula for computing; in neural networks; in neurons; in recurrent neural networks; in word2vec

**Original Spanish:** (empty)

**🆕 LLM Generated:** activaciones: en sistemas codificador-decodificador; fórmula para calcular; en redes neuronales; en neuronas; en redes neuronales recurentes; en word2vec ±

**Confidence:** 0.05

---

### Issue 475 ✅ FIXED

**English:** active-symbol architecture

**Original Spanish:** (empty)

**🆕 LLM Generated:** arquitectura de símbolo activo ±

**Confidence:** 0.05

---

### Issue 476 ✅ FIXED

**English:** adversarial examples: for computer vision; for deep Q-learning systems; for natural-language processing systems; for self-driving cars; for speech-recognition systems

**Original Spanish:** (empty)

**🆕 LLM Generated:** ejemplos antagonistas: para visión por computadora; para sistemas de aprendizaje profundo Q; para sistemas de procesamiento de lenguaje natural; para automóviles autónomos; para sistemas de reconocimi...

**Confidence:** 0.05

---

### Issue 477 ✅ FIXED

**English:** AGI, see general or human-level AI

**Original Spanish:** problema 5: Si abc cambia a abd, ¿a qué cambia ace?

**🔍 Vector Search (0.32):** problema 5: Si abc cambia a abd, ¿a qué cambia ace?

**✨ LLM Repair:** AI, ver general o IA a nivel humano ±

**Confidence:** 0.1520882248878479

---

### Issue 478 ✅ FIXED

**English:** Agüera y Arcas, Blaise

**Original Spanish:** (empty)

**🆕 LLM Generated:** Agurera y Arcas, Blasio ±

**Confidence:** 0.05

---

### Issue 479 ✅ FIXED

**English:** AI, see artificial intelligence

**Original Spanish:** (empty)

**🆕 LLM Generated:** IA ±

**Confidence:** 0.05

---

### Issue 480 ✅ FIXED

**English:** AI Singularity, see Singularity

**Original Spanish:** (empty)

**🆕 LLM Generated:** Canto de la Inteligencia Artificial, véase Canto ±

**Confidence:** 0.05

---

### Issue 481 ✅ FIXED

**English:** Allen Institute for Artificial Intelligence; science questions data set

**Original Spanish:** (empty)

**🆕 LLM Generated:** Instituto de Inteligencia ArtificIAL Allen; conjunto de datos de preguntas científicas ±

**Confidence:** 0.05

---

### Issue 482 ✅ FIXED

**English:** AlphaGo; intelligence of; learning in

**Original Spanish:** (empty)

**🆕 LLM Generated:** AlphaGo; inteligencia de; aprendizaje en ±

**Confidence:** 0.05

---

### Issue 483 ✅ FIXED

**English:** Amazon Mechanical Turk; origin of name

**Original Spanish:** (empty)

**🆕 LLM Generated:** El nombre Amazon Mechanical Turk tiene su origen en... ±

**Confidence:** 0.05

---

### Issue 484 📏 OVER-LONG (FIXED)

**English:** American Civil Liberties Union (ACLU)

**Original Spanish:** Para ambos problemas es necesario reconocer nuevos conceptos sobre la marcha, una habilidad de la qu...

**📏 LLM Resized:** Unión Americana de Libertades Civiles ±

**Confidence:** 0.15

---

### Issue 485 ✅ FIXED

**English:** artificial general intelligence, see general or human-level AI

**Original Spanish:** Un aspecto esencial de la inteligencia humana —del que no se habla mucho en la IA hoy en día— es su capacidad de percibir y reflexionar sobre el propio pensamiento.

**🔍 Vector Search (0.36):** Un aspecto esencial de la inteligencia humana —del que no se habla mucho en la IA hoy en día— es su capacidad de percibir y reflexionar sobre el propio pensamiento.

**✨ LLM Repair:** inteligencia general artificial, véase inteligencia o IA humana ±

**Confidence:** 0.3648875653743744

---

### Issue 486 ✅ FIXED

**English:** artificial intelligence: beneficial; bias in; creativity in; definition of; explainability; general or human-level; moral; origin of term; regulation of; relationship to deep learning and machine lear...

**Original Spanish:** En psicología, esto se llama metacognición. ¿Alguna vez han intentado en vano resolver un problema y han acabado reconociendo que estaban repitiendo los mismos procesos de pensamiento infructuosos?

**🔍 Vector Search (0.51):** En psicología, esto se llama metacognición. ¿Alguna vez han intentado en vano resolver un problema y han acabado reconociendo que estaban repitiendo los mismos procesos de pensamiento infructuosos?

**✨ LLM Repair:** inteligencia artificial: beneficiosa; sesgo en; creatividad en; definición de; explicabilidad; general o a nivel humano; moral; origen del término; regulación de; relación con el aprendizaje profundo ...

**Confidence:** 0.374267041683197

---

### Issue 487 📏 OVER-LONG (FIXED)

**English:** Asimov, Isaac; fundamental Rules of Robotics

**Original Spanish:** A mí me pasa con frecuencia, pero, una vez que identifico el patrón, a veces consigo salir del atasc...

**📏 LLM Resized:** Reglas fundamentales de la robótica según Asimov, Isaac ±

**Confidence:** 0.15

---

### Issue 488 ✅ FIXED

**English:** Atari video games; see also Breakout

**Original Spanish:** Figura 48. Cuatro ejemplos sencillos de «pasear a un perro».

**🔍 Vector Search (0.31):** Figura 48. Cuatro ejemplos sencillos de «pasear a un perro».

**✨ LLM Repair:** Videojuegos Atari; véase también Desentierre ±

**Confidence:** 0.27149930596351624

---

### Issue 489 ✅ FIXED

**English:** automated image captioning

**Original Spanish:** (empty)

**🆕 LLM Generated:** "La generación automática de leyendas para imágenes." ±

**Confidence:** 0.05

---

### Issue 490 ✅ FIXED

**English:** autonomous vehicles, see self-driving cars

**Original Spanish:** (empty)

**🆕 LLM Generated:** vehículos autónomos ±

**Confidence:** 0.05

---

### Issue 491 📏 OVER-LONG (FIXED)

**English:** back-propagation; in convolutional neural networks; in deep reinforcement learning

**Original Spanish:** James Marshall, por aquel entonces estudiante de posgrado en el grupo de investigación de Douglas Ho...

**📏 LLM Resized:** propagación hacia atrás; en redes neuronales convolucionales; en aprendizaje reforzado profundo ±

**Confidence:** 0.15

---

### Issue 492 ✅ FIXED

**English:** bias; in face recognition; in word vectors

**Original Spanish:** (empty)

**🆕 LLM Generated:** sesgo; en el reconocimiento facial; en vectores de palabras ±

**Confidence:** 0.05

---

### Issue 493 ✅ FIXED

**English:** bilingual evaluation understudy (BLEU)

**Original Spanish:** (empty)

**🆕 LLM Generated:** Evaluación bilingüe en estudio ±

**Confidence:** 0.05

---

### Issue 494 ✅ FIXED

**English:** board positions; in checkers; in chess; in Go

**Original Spanish:** (empty)

**🆕 LLM Generated:** En ajedrez; en damas; en jaque mate ±

**Confidence:** 0.05

---

### Issue 495 📏 OVER-LONG (FIXED)

**English:** Breakout; deep Q-learning for; transfer learning on

**Original Spanish:** Mis investigaciones actuales se centran en el desarrollo de un sistema de IA que utilice la analogía...

**📏 LLM Resized:** Romper filas; aprendizaje profundo de Q para; aprendizaje de transferencia en ±

**Confidence:** 0.15

---

### Issue 496 ✅ FIXED

**English:** Centre for the Study of Existential Risk

**Original Spanish:** «Estamos verdaderamente muy lejos»

**🔍 Vector Search (0.23):** «Estamos verdaderamente muy lejos»

**✨ LLM Repair:** Centro para el Estudio del Riesgo Existencial ±

**Confidence:** 0.22779569029808044

---

### Issue 497 ✅ FIXED

**English:** checkers; see also Samuel’s checkers-playing program

**Original Spanish:** (empty)

**🆕 LLM Generated:** ajedrez; véase también el programa de ajedrez de Samuel ±

**Confidence:** 0.05

---

### Issue 498 ✅ FIXED

**English:** chess; see also Deep Blue

**Original Spanish:** (empty)

**🆕 LLM Generated:** ajedrez; véase también Profundo Azul ±

**Confidence:** 0.05

---

### Issue 499 ✅ FIXED

**English:** classification; in convolutional neural networks

**Original Spanish:** (empty)

**🆕 LLM Generated:** Clasificación; en redes neuronales convolucionales ±

**Confidence:** 0.05

---

### Issue 500 ✅ FIXED

**English:** classification module

**Original Spanish:** (empty)

**🆕 LLM Generated:** "Módulo de clasificación" ±

**Confidence:** 0.05

---

### Issue 501 ✅ FIXED

**English:** common sense; in babies; knowledge in Cyc; for self-driving cars

**Original Spanish:** (empty)

**🆕 LLM Generated:** Sensatez común; en bebés; conocimiento en Cyc; para coches autónomos ±

**Confidence:** 0.05

---

### Issue 502 ✅ FIXED

**English:** concepts as mental simulations

**Original Spanish:** (empty)

**🆕 LLM Generated:** Conceptos como simulaciones mentales ±

**Confidence:** 0.05

---

### Issue 503 ✅ FIXED

**English:** connectionist networks, see connectionism

**Original Spanish:** (empty)

**🆕 LLM Generated:** Redes conexionistas, véase connectionismo ±

**Confidence:** 0.05

---

### Issue 504 ✅ FIXED

**English:** ConvNet, see convolutional neural networks

**Original Spanish:** (empty)

**🆕 LLM Generated:** Redes Neuronales Convolucionales (RNC) ±

**Confidence:** 0.05

---

### Issue 505 ✅ FIXED

**English:** convolutional neural networks; abstraction abilities; activation maps in; classification module; commercial applications of; comparison with humans on object recognition; in deep Q-learning; fully con...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Redes neuronales convolucionales; habilidades de abstracción; mapas de activación en; módulo de clasificación; aplicaciones comerciales de; comparación con humanos en el reconocimiento de objetos; en ...

**Confidence:** 0.05

---

### Issue 506 ✅ FIXED

**English:** Copycat; letter-string microworld

**Original Spanish:** (empty)

**🆕 LLM Generated:** Copia; mundo micro de cadena de letras ±

**Confidence:** 0.05

---

### Issue 507 ✅ FIXED

**English:** core knowledge; for self-driving cars

**Original Spanish:** (empty)

**🆕 LLM Generated:** Conocimiento fundamental; para coches autónomos ±

**Confidence:** 0.05

---

### Issue 508 ✅ FIXED

**English:** DARPA, see Defense Advanced Research Projects Agency

**Original Spanish:** (empty)

**🆕 LLM Generated:** Agencia de Proyectos de Investigación Avanzada de Defensa ±

**Confidence:** 0.05

---

### Issue 509 ✅ FIXED

**English:** Dartmouth AI workshop

**Original Spanish:** (empty)

**🆕 LLM Generated:** Taller de Inteligencia Artificial de Dartmouth ±

**Confidence:** 0.05

---

### Issue 510 ✅ FIXED

**English:** deep learning; adversarial examples for, see adversarial examples; as “Clever Hans”; difference from human perception; explainability of; inspiration from neuroscience; lack of reliability; as narrow ...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Profundo aprendizaje; ejemplos adversarios para, véase ejemplos adversarios; como "Hans el Listo"; diferencia con la percepción humana; explicabilidad de; inspiración en neurociencia; falta de fiabili...

**Confidence:** 0.05

---

### Issue 511 ✅ FIXED

**English:** DeepMind; acquisition by Google; see also AlphaGo; Breakout

**Original Spanish:** (empty)

**🆕 LLM Generated:** ProfundidadMente; adquisición por Google; véase también AlphaGo; Rompecabezas ±

**Confidence:** 0.05

---

### Issue 512 ✅ FIXED

**English:** deep neural networks, see deep learning

**Original Spanish:** (empty)

**🆕 LLM Generated:** redes neuronales profundas, véase aprendizaje profundo ±

**Confidence:** 0.05

---

### Issue 513 ✅ FIXED

**English:** deep Q-learning; adversarial examples for; on Breakout; compared with random search; convolutional network in; on Go; transfer abilities

**Original Spanish:** (empty)

**🆕 LLM Generated:** Profundo aprendizaje por refuerzo; ejemplos adversariales para; en Breakout; comparado con búsqueda aleatoria; red convolucional en; en Go; habilidades de transferencia ±

**Confidence:** 0.05

---

### Issue 514 ✅ FIXED

**English:** Defense Advanced Research Projects Agency

**Original Spanish:** (empty)

**🆕 LLM Generated:** Agencia de Investigación de Proyectos Avanzados de Defensa ±

**Confidence:** 0.05

---

### Issue 515 ✅ FIXED

**English:** embodiment hypothesis

**Original Spanish:** (empty)

**🆕 LLM Generated:** hipótesis de encarnación ±

**Confidence:** 0.05

---

### Issue 516 ✅ FIXED

**English:** EMI, see Experiments in Musical Intelligence

**Original Spanish:** (empty)

**🆕 LLM Generated:** Experimentos en Inteligencia Musical ±

**Confidence:** 0.05

---

### Issue 517 ✅ FIXED

**English:** encoder-decoder system

**Original Spanish:** (empty)

**🆕 LLM Generated:** sistema codificador-desencodificador ±

**Confidence:** 0.05

---

### Issue 518 ✅ FIXED

**English:** Eugene Goostman (chatbot)

**Original Spanish:** (empty)

**🆕 LLM Generated:** Eugene Goostman (robot de chat) ±

**Confidence:** 0.05

---

### Issue 519 ✅ FIXED

**English:** Experiments in Musical Intelligence

**Original Spanish:** (empty)

**🆕 LLM Generated:** Experimentos en Inteligencia Musical ±

**Confidence:** 0.05

---

### Issue 520 ✅ FIXED

**English:** exploration versus exploitation

**Original Spanish:** (empty)

**🆕 LLM Generated:** Exploración frente a explotación ±

**Confidence:** 0.05

---

### Issue 521 ✅ FIXED

**English:** face recognition; adversarial attacks on; biases in; ethics of

**Original Spanish:** (empty)

**🆕 LLM Generated:** reconocimiento facial; ataques adversarios en; sesgos en; ética de ±

**Confidence:** 0.05

---

### Issue 522 ✅ FIXED

**English:** Future of Humanity Institute

**Original Spanish:** (empty)

**🆕 LLM Generated:** Instituto del Futuro de la Humanidad ±

**Confidence:** 0.05

---

### Issue 523 ✅ FIXED

**English:** Future of Life Institute

**Original Spanish:** (empty)

**🆕 LLM Generated:** Instituto del Futuro de la Vida ±

**Confidence:** 0.05

---

### Issue 524 ✅ FIXED

**English:** game tree; in checkers; in chess; in Go

**Original Spanish:** (empty)

**🆕 LLM Generated:** Juego de damas; en jaque; ajedrez; Go ±

**Confidence:** 0.05

---

### Issue 525 ✅ FIXED

**English:** GEB, see Gödel, Escher, Bach

**Original Spanish:** (empty)

**🆕 LLM Generated:** GEB, véase Gödel, Escher, Bach ±

**Confidence:** 0.05

---

### Issue 526 ✅ FIXED

**English:** general or human-level AI

**Original Spanish:** (empty)

**🆕 LLM Generated:** Inteligencia Artificial general o a nivel humano ±

**Confidence:** 0.05

---

### Issue 527 ✅ FIXED

**English:** General Problem Solver

**Original Spanish:** (empty)

**🆕 LLM Generated:** Resolutor de Problemas Generales ±

**Confidence:** 0.05

---

### Issue 528 ✅ FIXED

**English:** Go (board game); see also AlphaGo

**Original Spanish:** (empty)

**🆕 LLM Generated:** Juego de mesa; véase también AlphaGo ±

**Confidence:** 0.05

---

### Issue 529 ✅ FIXED

**English:** Gödel, Escher, Bach (book)

**Original Spanish:** (empty)

**🆕 LLM Generated:** "Gödel, Escher, Bach" ±

**Confidence:** 0.05

---

### Issue 530 ✅ FIXED

**English:** Google DeepMind, see DeepMind

**Original Spanish:** (empty)

**🆕 LLM Generated:** Google DeepMind, ver DeepMind ±

**Confidence:** 0.05

---

### Issue 531 ✅ FIXED

**English:** Google Translate; see also neural machine translation

**Original Spanish:** (empty)

**🆕 LLM Generated:** Traducción de Google; véase también traducción por machine learning ±

**Confidence:** 0.05

---

### Issue 532 ✅ FIXED

**English:** GPS, see General Problem Solver

**Original Spanish:** (empty)

**🆕 LLM Generated:** SGS, ver Solucionador General de Problemas ±

**Confidence:** 0.05

---

### Issue 533 ✅ FIXED

**English:** GPUs, see graphical processing units

**Original Spanish:** (empty)

**🆕 LLM Generated:** "Unidades de procesamiento gráfico (UPGs)" ±

**Confidence:** 0.05

---

### Issue 534 ✅ FIXED

**English:** graphical processing units

**Original Spanish:** (empty)

**🆕 LLM Generated:** Unidades de Procesamiento Gráfico ±

**Confidence:** 0.05

---

### Issue 535 ✅ FIXED

**English:** hidden units, see hidden layers

**Original Spanish:** (empty)

**🆕 LLM Generated:** Unidades ocultas, vea capas ocultas ±

**Confidence:** 0.05

---

### Issue 536 ✅ FIXED

**English:** human-level AI, see general or human-level AI

**Original Spanish:** (empty)

**🆕 LLM Generated:** IA de nivel humano, véase IA general o IA de nivel humano ±

**Confidence:** 0.05

---

### Issue 537 ✅ FIXED

**English:** ImageNet; cheating incident; competitions; human performance on; localization challenge; pretraining on; relation to top-1 accuracy metric; top-5 accuracy metric; WordNet

**Original Spanish:** (empty)

**🆕 LLM Generated:** Imagenet; incidente de fraude; competencias; rendimiento humano en ellas; desafío de localización; pretécnica sobre él; relación con la métrica de precisión superior al 1%; la métrica de precisión sup...

**Confidence:** 0.05

---

### Issue 538 ✅ FIXED

**English:** imitation game, see Turing test

**Original Spanish:** (empty)

**🆕 LLM Generated:** Juego de imitación, vea la prueba de Turing ±

**Confidence:** 0.05

---

### Issue 539 ✅ FIXED

**English:** intuitive knowledge, see core knowledge

**Original Spanish:** (empty)

**🆕 LLM Generated:** Conocimiento intuitivo, ver conocimiento nuclear ±

**Confidence:** 0.05

---

### Issue 540 ✅ FIXED

**English:** Jeopardy!; IBM Watson’s match

**Original Spanish:** (empty)

**🆕 LLM Generated:** ¡Peligro!; El encuentro de IBM Watson ±

**Confidence:** 0.05

---

### Issue 541 ✅ FIXED

**English:** jobs, see unemployment

**Original Spanish:** (empty)

**🆕 LLM Generated:** trabajos, véase desempleo ±

**Confidence:** 0.05

---

### Issue 542 ✅ FIXED

**English:** long short-term memory

**Original Spanish:** (empty)

**🆕 LLM Generated:** memoria de largo plazo ±

**Confidence:** 0.05

---

### Issue 543 ✅ FIXED

**English:** long tail; see also long-tail problem

**Original Spanish:** (empty)

**🆕 LLM Generated:** Cola larga; véase también problema de la cola larga ±

**Confidence:** 0.05

---

### Issue 544 ✅ FIXED

**English:** LSTM, see long short-term memory

**Original Spanish:** (empty)

**🆕 LLM Generated:** LSTM, véase memoria de corto plazo a largo plazo ±

**Confidence:** 0.05

---

### Issue 545 ✅ FIXED

**English:** machine learning; adversarial, see adversarial learning; bias in, see bias; interpretable, see explainable AI; overfitting in, see overfitting; transfer learning in, see transfer learning

**Original Spanish:** (empty)

**🆕 LLM Generated:** aprendizaje automático; adversarial, véase aprendizaje adversarial; sesgo en, véase sesgo; interpretable, véase IA explicable; sobreajuste en, véase sobreajuste; aprendizaje de transferencia en, véase...

**Confidence:** 0.05

---

### Issue 546 ✅ FIXED

**English:** machine morality, see moral AI

**Original Spanish:** (empty)

**🆕 LLM Generated:** Moralidad de la máquina ±

**Confidence:** 0.05

---

### Issue 547 ✅ FIXED

**English:** machine translation; comparison between humans and machines; evaluating; neural; statistical; see also Google Translate

**Original Spanish:** (empty)

**🆕 LLM Generated:** Traducción automática; comparación entre humanos y máquinas; evaluación; neural; estadística; véase también Google Traductora ±

**Confidence:** 0.05

---

### Issue 548 ✅ FIXED

**English:** Mechanical Turk, see Amazon Mechanical Turk

**Original Spanish:** (empty)

**🆕 LLM Generated:** El Turco Mecánico, véase Amazon Mechanical Turk ±

**Confidence:** 0.05

---

### Issue 549 ✅ FIXED

**English:** Metaphors We Live By (book)

**Original Spanish:** (empty)

**🆕 LLM Generated:** Las Metáforas en las que Vivimos ±

**Confidence:** 0.05

---

### Issue 550 ✅ FIXED

**English:** Monte Carlo tree search; roll-outs

**Original Spanish:** (empty)

**🆕 LLM Generated:** Búsqueda de árboles de Monte Carlo; simulaciones aleatorias ±

**Confidence:** 0.05

---

### Issue 551 ✅ FIXED

**English:** Mullainathan, Sendhil

**Original Spanish:** (empty)

**🆕 LLM Generated:** Mullainathan, Sendhil ±

**Confidence:** 0.05

---

### Issue 552 ✅ FIXED

**English:** multilayer neural networks; Minsky and Papert’s speculations on; see also neural networks

**Original Spanish:** (empty)

**🆕 LLM Generated:** Redes neuronales de múltiples capas; especulaciones de Minsky y Papert sobre; véase también redes neuronales ±

**Confidence:** 0.05

---

### Issue 553 ✅ FIXED

**English:** natural-language processing: adversarial attacks on; challenges for; definition of; rule-based approaches to; statistical approaches to; see also machine translation; question answering; reading compr...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Procesamiento de lenguaje natural: ataques adversariales en; desafíos para; definición de; enfoques basados en reglas para; enfoques estadísticos para; véase también traducción automática; clasificaci...

**Confidence:** 0.05

---

### Issue 554 ✅ FIXED

**English:** neural machine translation; see also Google Translate; machine translation

**Original Spanish:** (empty)

**🆕 LLM Generated:** Traducción automática neuronal; también ver Google Traductora; traducción automática ±

**Confidence:** 0.05

---

### Issue 555 ✅ FIXED

**English:** neural networks: activations in; classification in; convolutional, see convolutional neural networks; deep, see deep learning; depth of; hidden layers; learning in; multilayer; recurrent; 199–200; uni...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Redes neuronales: activaciones en; clasificación en; convolucionales, véase redes neuronales convolucionales; profundas, véase aprendizaje profundo; profundidad de; capas ocultas; aprendizaje en; mult...

**Confidence:** 0.05

---

### Issue 556 ✅ FIXED

**English:** NLP, see natural-language processing

**Original Spanish:** (empty)

**🆕 LLM Generated:** Procesamiento de lenguaje natural ±

**Confidence:** 0.05

---

### Issue 557 ✅ FIXED

**English:** object recognition; in the brain; comparing ConvNets and humans on; see also ImageNet; PASCAL Visual Object Classes competition

**Original Spanish:** (empty)

**🆕 LLM Generated:** Reconocimiento de objetos; en el cerebro; comparando ConvNets y humanos en; véase también ImageNet; Competencia de clases visuales de objetos Pascal ±

**Confidence:** 0.05

---

### Issue 558 ✅ FIXED

**English:** PASCAL Visual Object Classes competition

**Original Spanish:** (empty)

**🆕 LLM Generated:** Concurso de Clases de Objetos Visuales Pascal ±

**Confidence:** 0.05

---

### Issue 559 ✅ FIXED

**English:** perceptron learning algorithm

**Original Spanish:** (empty)

**🆕 LLM Generated:** álgoritmo de aprendizaje del perceptrón ±

**Confidence:** 0.05

---

### Issue 560 ✅ FIXED

**English:** perceptrons; analogy with neurons; compared with multilayer neural networks; for handwritten digit recognition; inputs; learning algorithm; limitations of; threshold; as subsymbolic AI approach; weigh...

**Original Spanish:** (empty)

**🆕 LLM Generated:** perceptrones; analogía con neuronas; comparados con redes neuronales de múltiples capas; para el reconocimiento de dígitos escritos a mano; entradas; algoritmo de aprendizaje; limitaciones de; umbral;...

**Confidence:** 0.05

---

### Issue 561 ✅ FIXED

**English:** Q-learning; see also deep Q-learning

**Original Spanish:** (empty)

**🆕 LLM Generated:** El aprendizaje por refuerzo; véase también aprendizaje profundo por refuerzo ±

**Confidence:** 0.05

---

### Issue 562 ✅ FIXED

**English:** question answering; 214–15; adversarial attacks on; see also IBM Watson; reading comprehension; Stanford Question-Answering Dataset; Winograd schemas

**Original Spanish:** (empty)

**🆕 LLM Generated:** Preguntas y respuestas; 214-15; ataques adversariales en contra de; véase también IBM Watson; comprensión lectora; Conjunto de datos de Preguntas y Respuestas de Stanford; esquemas de Winograd ±

**Confidence:** 0.05

---

### Issue 563 ✅ FIXED

**English:** reading comprehension

**Original Spanish:** (empty)

**🆕 LLM Generated:** Comprensión lectora ±

**Confidence:** 0.05

---

### Issue 564 ✅ FIXED

**English:** recurrent neural networks; 199–200

**Original Spanish:** (empty)

**🆕 LLM Generated:** redes neuronales recurrentes; 199-200 ±

**Confidence:** 0.05

---

### Issue 565 ✅ FIXED

**English:** reinforcement learning; actions of agent in; contrast with supervised learning; deep Q-learning, see deep Q-learning; discounting in; episode; epsilon-greedy method for; exploration versus exploitatio...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Aprendizaje por refuerzo; acciones del agente en; contraste con el aprendizaje supervisado; aprendizaje profundo de Q, ver aprendizaje profundo de Q; descuento en; episodio; método epsilon-greedy para...

**Confidence:** 0.05

---

### Issue 566 ✅ FIXED

**English:** Samuel’s checkers-playing program; alpha-beta pruning in; evaluation function

**Original Spanish:** (empty)

**🆕 LLM Generated:** El programa de damas de Samuel; poda alfa-beta en la función de evaluación ±

**Confidence:** 0.05

---

### Issue 567 ✅ FIXED

**English:** self-driving cars; 117–18; 267–71; adversarial examples for; benefits of; ethics for; geofencing for; levels of autonomy for; partial versus full autonomy for; safety drivers for; training data for

**Original Spanish:** (empty)

**🆕 LLM Generated:** Coches autónomos; 117-18; 267-71; ejemplos adversarios para; beneficios de; ética para; geoabarrotamiento para; niveles de autonomía para; autonomía parcial versus completa para; conductores de seguri...

**Confidence:** 0.05

---

### Issue 568 ✅ FIXED

**English:** semantic space of words

**Original Spanish:** (empty)

**🆕 LLM Generated:** Espacio semántico de las palabras ±

**Confidence:** 0.05

---

### Issue 569 ✅ FIXED

**English:** sentiment classification

**Original Spanish:** (empty)

**🆕 LLM Generated:** Clasificación de sentimientos ±

**Confidence:** 0.05

---

### Issue 570 ✅ FIXED

**English:** Show and Tell (image-captioning system)

**Original Spanish:** (empty)

**🆕 LLM Generated:** Mostrar y Contar ±

**Confidence:** 0.05

---

### Issue 571 ✅ FIXED

**English:** Singularity University

**Original Spanish:** (empty)

**🆕 LLM Generated:** Unidad de Singularidad ±

**Confidence:** 0.05

---

### Issue 572 ✅ FIXED

**English:** speech recognition; adversarial examples for; word-error rate in

**Original Spanish:** (empty)

**🆕 LLM Generated:** Reconocimiento de la palabra hablada; ejemplos adversos para; tasa de error de palabra en ±

**Confidence:** 0.05

---

### Issue 573 ✅ FIXED

**English:** Stanford Question Answering Dataset (SQuAD); human accuracy on

**Original Spanish:** (empty)

**🆕 LLM Generated:** La base de datos de preguntas y respuestas de Stanford (SQuAD): precisión humana ±

**Confidence:** 0.05

---

### Issue 574 ✅ FIXED

**English:** statistical machine translation

**Original Spanish:** (empty)

**🆕 LLM Generated:** traducción estadística por máquina ±

**Confidence:** 0.05

---

### Issue 575 ✅ FIXED

**English:** strong AI; see also general or human-level AI

**Original Spanish:** (empty)

**🆕 LLM Generated:** Inteligencia artificial avanzada; véase también inteligencia general o de nivel humano ±

**Confidence:** 0.05

---

### Issue 576 ✅ FIXED

**English:** subsymbolic AI; contrast with symbolic methods; integration with symbolic methods

**Original Spanish:** (empty)

**🆕 LLM Generated:** Inteligencia Artificial subsimbólica; contraste con métodos simbólicos; integración con métodos simbólicos ±

**Confidence:** 0.05

---

### Issue 577 ✅ FIXED

**English:** Summer Vision Project (MIT)

**Original Spanish:** (empty)

**🆕 LLM Generated:** Proyecto de Visión de Verano ±

**Confidence:** 0.05

---

### Issue 578 ✅ FIXED

**English:** superhuman intelligence

**Original Spanish:** (empty)

**🆕 LLM Generated:** inteligencia sobrehumana ±

**Confidence:** 0.05

---

### Issue 579 ✅ FIXED

**English:** superintelligence, see superhuman intelligence

**Original Spanish:** (empty)

**🆕 LLM Generated:** superintelecto, ver inteligencia sobrehumana ±

**Confidence:** 0.05

---

### Issue 580 ✅ FIXED

**English:** Superintelligence (book)

**Original Spanish:** (empty)

**🆕 LLM Generated:** Superintelectualidad ±

**Confidence:** 0.05

---

### Issue 581 ✅ FIXED

**English:** supervised learning; contrast with human learning; contrast with reinforcement learning; in IBM Watson

**Original Spanish:** (empty)

**🆕 LLM Generated:** Aprendizaje supervisado; en contraste con el aprendizaje humano; en contraste con el aprendizaje por refuerzo; en IBM Watson ±

**Confidence:** 0.05

---

### Issue 582 ✅ FIXED

**English:** support vector machines

**Original Spanish:** (empty)

**🆕 LLM Generated:** Máquinas de Vectores de Soportes ±

**Confidence:** 0.05

---

### Issue 583 ✅ FIXED

**English:** symbolic AI; contrast with subsymbolic methods; integration with subsymbolic methods

**Original Spanish:** (empty)

**🆕 LLM Generated:** Inteligencia Artificial Simbólica; Contraposición con Métodos Subsimbólicos; Integración con Métodos Subsimbólicos ±

**Confidence:** 0.05

---

### Issue 584 ✅ FIXED

**English:** temporal difference learning; see also reinforcement learning

**Original Spanish:** (empty)

**🆕 LLM Generated:** aprendizaje basado en diferencias temporales; véase también aprendizaje por refuerzo ±

**Confidence:** 0.05

---

### Issue 585 ✅ FIXED

**English:** training, see supervised learning

**Original Spanish:** (empty)

**🆕 LLM Generated:** "Entrenamiento, véase aprendizaje supervisado"

NOTE:
This is a direct translation without adding any notes or changing the tone and style. The English text provided uses technical terms from machine ...

**Confidence:** 0.05

---

### Issue 586 ✅ FIXED

**English:** transfer learning; for Breakout

**Original Spanish:** (empty)

**🆕 LLM Generated:** Aprendizaje transferido; para Escape ±

**Confidence:** 0.05

---

### Issue 587 ✅ FIXED

**English:** translation, see machine translation

**Original Spanish:** (empty)

**🆕 LLM Generated:** traducción, ver traducción por máquina ±

**Confidence:** 0.05

---

### Issue 588 ✅ FIXED

**English:** Turing test; Kurzweil and Kapor wager on; Kurzweil’s predictions for

**Original Spanish:** (empty)

**🆕 LLM Generated:** Prueba de Turing; apuesta de Kurzweil y Kapor; predicciones de Kurzweil para ±

**Confidence:** 0.05

---

### Issue 589 ✅ FIXED

**English:** understanding: in analogy; ascribing to computers; in automated image captioning; for creativity; in Cyc; in deep learning; in humans; in IBM Watson; in machine translation; for morality; for natural-...

**Original Spanish:** (empty)

**🆕 LLM Generated:** Entendimiento: en analogía; atribuyendo a computadoras; en la descripción automática de imágenes; para creatividad; en Cyc; en aprendizaje profundo; en humanos; en IBM Watson; en traducción automática...

**Confidence:** 0.05

---

### Issue 590 ✅ FIXED

**English:** unsupervised learning

**Original Spanish:** (empty)

**🆕 LLM Generated:** aprendizaje no supervisado ±

**Confidence:** 0.05

---

### Issue 591 ✅ FIXED

**English:** Watson, see IBM Watson

**Original Spanish:** (empty)

**🆕 LLM Generated:** "Watson, vea a IBM Watson" ±

**Confidence:** 0.05

---

### Issue 592 ✅ FIXED

**English:** weak AI; see also strong AI

**Original Spanish:** (empty)

**🆕 LLM Generated:** IA débil; véase también IA fuerte ±

**Confidence:** 0.05

---

### Issue 593 ✅ FIXED

**English:** word embeddings; see also word vectors

**Original Spanish:** (empty)

**🆕 LLM Generated:** incrustaciones de palabras; véase también vectores de palabras ±

**Confidence:** 0.05

---

### Issue 594 ✅ FIXED

**English:** word vectors; analogies using; biases in; debiasing

**Original Spanish:** (empty)

**🆕 LLM Generated:** vector de palabras; Analogías utilizando; sesgos en; desvíos ±

**Confidence:** 0.05

---

### Issue 595 ✅ FIXED

**English:** 1.  The Roots of Artificial Intelligence

**Original Spanish:** (empty)

**🆕 LLM Generated:** Los Orígenes de la Inteligencia Artificial ±

**Confidence:** 0.05

---

### Issue 596 ✅ FIXED

**English:** 2.  Neural Networks and the Ascent of Machine Learning

**Original Spanish:** (empty)

**🆕 LLM Generated:** Redes neuronales y la ascensión del aprendizaje automático ±

**Confidence:** 0.05

---

### Issue 597 ✅ FIXED

**English:** Part II.  Looking and Seeing

**Original Spanish:** (empty)

**🆕 LLM Generated:** Part II. Mirar y Ver ±

**Confidence:** 0.05

---

### Issue 598 ✅ FIXED

**English:** 4.  Who, What, When, Where, Why

**Original Spanish:** (empty)

**🆕 LLM Generated:** ¿Quién? ¿Qué? ¿Cuándo? ¿Dónde? ¿Por qué? ±

**Confidence:** 0.05

---

### Issue 599 ✅ FIXED

**English:** 5.  ConvNets and ImageNet

**Original Spanish:** (empty)

**🆕 LLM Generated:** 5. ConvNets y ImageNet ±

**Confidence:** 0.05

---

### Issue 600 ✅ FIXED

**English:** 6.  A Closer Look at Machines That Learn

**Original Spanish:** (empty)

**🆕 LLM Generated:** 6. Un examen más detallado de las máquinas que aprenden ±

**Confidence:** 0.05

---

### Issue 601 ✅ FIXED

**English:** 7.  On Trustworthy and Ethical AI

**Original Spanish:** (empty)

**🆕 LLM Generated:** "7. Acerca de la Inteligencia Artificial Fiable y Ética." ±

**Confidence:** 0.05

---

### Issue 602 ✅ FIXED

**English:** Part III.  Learning to Play

**Original Spanish:** (empty)

**🆕 LLM Generated:** Tercera Parte. Aprender a Jugar ±

**Confidence:** 0.05

---

### Issue 603 ✅ FIXED

**English:** 8.  Rewards for Robots

**Original Spanish:** (empty)

**🆕 LLM Generated:** 8. Recompensas para robots ±

**Confidence:** 0.05

---

### Issue 604 ✅ FIXED

**English:** Part IV.  Artificial Intelligence Meets Natural Language

**Original Spanish:** (empty)

**🆕 LLM Generated:** Cuarta parte. Inteligencia Artificial se encuentra con el Lenguaje Natural ±

**Confidence:** 0.05

---

### Issue 605 ✅ FIXED

**English:** 11.  Words, and the Company They Keep

**Original Spanish:** (empty)

**🆕 LLM Generated:** "11. Palabras, y la Compañía que Mantienen"

The Spanish version maintains the same structure and tone as the English original, with "Palabras" translating to "Words," "Company" to "Compañía," and "Ke...

**Confidence:** 0.05

---

### Issue 606 ✅ FIXED

**English:** 12.  Translation as Encoding and Decoding

**Original Spanish:** (empty)

**🆕 LLM Generated:** 12. Traducción como Codificación y Descodificación ±

**Confidence:** 0.05

---

### Issue 607 ✅ FIXED

**English:** Part V.  The Barrier of Meaning

**Original Spanish:** (empty)

**🆕 LLM Generated:** Parte V. La Barrera del Significado ±

**Confidence:** 0.05

---

### Issue 608 ✅ FIXED

**English:** 14.  On Understanding

**Original Spanish:** (empty)

**🆕 LLM Generated:** "La Comprensión"

NOTE: The provided English text is too short to maintain any specific tone or style in Spanish. However, I've translated it literally as "The Understanding". If you have a longer pas...

**Confidence:** 0.05

---

### Issue 609 ✅ FIXED

**English:** 15.  Knowledge, Abstraction, and Analogy in Artificial Intelligence

**Original Spanish:** (empty)

**🆕 LLM Generated:** 15. Conocimiento, Abstracción y Análogía en Inteligencia Artificial ±

**Confidence:** 0.05

---

### Issue 610 ✅ FIXED

**English:** 16.  Questions, Answers, and Speculations

**Original Spanish:** Sobre Melania Mitchell

**🔍 Vector Search (0.25):** Sobre Melania Mitchell

**✨ LLM Repair:** 16. Preguntas, Respuestas y Especulaciones ±

**Confidence:** 0.18150416016578674

---

### Issue 611 ✅ FIXED

**English:** Also by Melanie Mitchell

**Original Spanish:** (empty)

**🆕 LLM Generated:** Tampoco por Melanie Mitchell ±

**Confidence:** 0.05

---

### Issue 612 ✅ FIXED

**English:** A Note About the Author

**Original Spanish:** (empty)

**🆕 LLM Generated:** Una Nota Sobre el Autor ±

**Confidence:** 0.05

---

### Issue 613 ✅ FIXED

**English:** 120 Broadway, New York 10271

**Original Spanish:** (empty)

**🆕 LLM Generated:** 120 Broadway, Nueva York 10271 ±

**Confidence:** 0.05

---

### Issue 614 ✅ FIXED

**English:** Our e-books may be purchased in bulk for promotional, educational, or business use. Please contact the Macmillan Corporate and Premium Sales Department at 1-800-221-7945, extension 5442, or by e-mail ...

**Original Spanish:** Corrección ortotipográfica: Victoria Parra Ortiz

**🔍 Vector Search (0.30):** Corrección ortotipográfica: Victoria Parra Ortiz

**✨ LLM Repair:** Es posible adquirir nuestros libros electrónicos en grandes cantidades con fines promocionales, educativos o comerciales. Por favor, póngase en contacto con el Departamento de Ventas Corporativas y Pr...

**Confidence:** 0.03018566593527794

---

## How to Fix Issues

If you see flagged pairs above:

1. Open the EPUB in Calibre or Sigil
2. Search for the English text shown above
3. Check if the Spanish translation below it is correct
4. Manually edit the Spanish text if needed

---
*Report generated by llm_verifier.py using Ollama*