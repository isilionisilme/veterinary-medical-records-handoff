from __future__ import annotations

# ruff: noqa: E501
from backend.app.application.documents.review_service import (
    _split_segment_into_observations_actions,
)


def test_split_segment_into_observations_actions_mixed_text() -> None:
    segment_text = "\n".join(
        [
            "Consulta 11/02/2026: dolor de oido y prurito auricular.",
            "Se diagnostica otitis externa y se realiza limpieza de oido.",
            "Se indica medicacion: gotas oticas 4 gotas cada 12 horas por 7 dias.",
        ]
    )

    observations, actions = _split_segment_into_observations_actions(segment_text=segment_text)

    assert observations == "dolor de oido y prurito auricular"
    assert actions is not None
    assert "Se diagnostica otitis externa y se realiza limpieza de oido" in actions
    assert "Se indica medicacion: gotas oticas 4 gotas cada 12 horas por 7 dias" in actions


def test_split_segment_into_observations_actions_observations_only() -> None:
    segment_text = "\n".join(
        [
            "Consulta 11/02/2026: apetito conservado y buen estado general.",
            "Temperatura normal y sin dolor a la palpacion.",
        ]
    )

    observations, actions = _split_segment_into_observations_actions(segment_text=segment_text)

    assert observations is not None
    assert "apetito conservado y buen estado general" in observations
    assert "Temperatura normal y sin dolor a la palpacion" in observations
    assert actions is None


def test_split_segment_into_observations_actions_actions_only() -> None:
    segment_text = "\n".join(
        [
            "Se administra antiinflamatorio intramuscular.",
            "Tratamiento: continuar medicacion oral por 5 dias.",
        ]
    )

    observations, actions = _split_segment_into_observations_actions(segment_text=segment_text)

    assert observations is None
    assert actions is not None
    assert "Se administra antiinflamatorio intramuscular" in actions
    assert "Tratamiento: continuar medicacion oral por 5 dias" in actions


def test_split_segment_into_observations_actions_empty_text() -> None:
    observations, actions = _split_segment_into_observations_actions(segment_text=" \n \n")

    assert observations is None
    assert actions is None


def test_split_segment_into_observations_actions_keeps_diagnostic_steps_in_observations() -> None:
    segment_text = "Saco sangre para test de leishmania y test de leishmania NEGATIVO."

    observations, actions = _split_segment_into_observations_actions(segment_text=segment_text)

    assert observations is not None
    assert "Saco sangre para test de leishmania y test de leishmania NEGATIVO" in observations
    assert actions is None


def test_split_segment_into_observations_actions_splits_inline_diagnostic_and_therapeutic_actions() -> (
    None
):
    segment_text = (
        "Saco sangre para test de leishmania, test de leishmania NEGATIVO Pongo vacuna letifend"
    )

    observations, actions = _split_segment_into_observations_actions(segment_text=segment_text)

    assert observations is not None
    assert "Saco sangre para test de leishmania, test de leishmania NEGATIVO" in observations
    assert actions is not None
    assert "Pongo vacuna letifend" in actions


def test_split_segment_into_observations_actions_docb32_expected_distribution() -> None:
    segment_text = (
        "le nota el ojo mejor, hace dos semanas de tratamiento "
        "No ha vuelto a tener heces blandas, solo hizo un día y sin medicación ahora mismo hace "
        "las heces duras. "
        "Vamos a pasar a nutro light como provocación para ver que tal las heces."
    )

    observations, actions = _split_segment_into_observations_actions(segment_text=segment_text)

    assert observations is not None
    assert "le nota el ojo mejor, hace dos semanas de tratamiento" in observations
    assert "No ha vuelto a tener heces blandas" in observations
    assert actions is not None
    assert "Vamos a pasar a nutro light como provocación para ver que tal las heces" in actions


def test_split_segment_into_observations_actions_docb33_expected_distribution() -> None:
    segment_text = (
        "Conjuntiva: inflamada con foliculos visibles en ambos ojos. "
        "Resto de exploración dentro de la normalidad y heces totalmente normales. "
        "Se recomienda seguir el tratamiento en ambos ojos con tobradex colirio 1 gota en cada ojo "
        "cada 8h durante 7-15 días más. "
        "Vamos a hacer provocación con su pienso anterior. "
        "Mezcla progresiva durante 1 semana y revision para volver a valorar. "
        "Cogemos cita para revisión en 1 semana y en 15 días."
    )

    observations, actions = _split_segment_into_observations_actions(segment_text=segment_text)

    assert observations is not None
    assert "Conjuntiva: inflamada con foliculos visibles en ambos ojos" in observations
    assert (
        "Resto de exploración dentro de la normalidad y heces totalmente normales" in observations
    )
    assert actions is not None
    assert "Se recomienda seguir el tratamiento en ambos ojos con tobradex colirio" in actions
    assert "Vamos a hacer provocación con su pienso anterior" in actions
    assert "Mezcla progresiva durante 1 semana y revision para volver a valorar" in actions
    assert "Cogemos cita para revisión en 1 semana y en 15 días" in actions


def test_split_segment_into_observations_actions_docb31_expected_distribution() -> None:
    segment_text = (
        "Conjuntivitis folicular el ojo derecho. "
        "Test de giardia: positivo!!. "
        "TRatamieto: tobradex colirio 1 gota en ojo derecho cada 8h durante 7-15 días. "
        "Si no dan problema y las heces son normales no vamosa tratarlo y en 3 meses repetiremos test "
        "de nuevo ya que el test puede dar positivo durante mucho tiempo. "
        "Si controlamos la conjuntivitis podemos esterilizarle. "
        "Si vuelve a tener heces feas volveremos a tratar."
    )

    observations, actions = _split_segment_into_observations_actions(segment_text=segment_text)

    assert observations is not None
    assert "Conjuntivitis folicular el ojo derecho" in observations
    assert "Test de giardia: positivo!!" in observations
    assert actions is not None
    assert "TRatamieto: tobradex colirio 1 gota en ojo derecho cada 8h durante 7-15 días" in actions
    assert "Si controlamos la conjuntivitis podemos esterilizarle" in actions


def test_split_segment_into_observations_actions_doca24_expected_distribution() -> None:
    segment_text = "\n".join(
        [
            "DÍA 17/07/2024 19:23:12 EN EL CENTRO COSTA AZAHAR",
            "GENERAL",
            "Anamnesis",
            "ACUDE PARA PONER LA VACUNA TETRAVALENTE.",
            "EN CASA COMENTAN QUE ESTÁ BIEN, DE MOMENTO CON LA NUEVA DIETA NO HA VUELTO A TENER PROBLEMAS.",
            "SE LE REALIZA EXPLORACIÓN FÍSICA COMPLETA: TODO NORMAL.",
            "Tratamiento",
            "PONEMOS LA VACUNA TETRAVALENTE CANINA.",
            "RECORDATORIOS",
            "Recordatorios vacunaciones",
            "Vacuna",
            "F. Próxima",
            "Aplicada",
            "VACUNACION TETRAVALENTE CANINA",
            "Sí",
        ]
    )

    observations, actions = _split_segment_into_observations_actions(segment_text=segment_text)

    assert observations is not None
    assert "DÍA 17/07/2024 19:23:12" not in observations
    assert "Anamnesis ACUDE PARA PONER LA VACUNA TETRAVALENTE" in observations
    assert (
        "EN CASA COMENTAN QUE ESTÁ BIEN, DE MOMENTO CON LA NUEVA DIETA NO HA VUELTO A TENER PROBLEMAS"
        in observations
    )
    assert "SE LE REALIZA EXPLORACIÓN FÍSICA COMPLETA: TODO NORMAL" in observations
    assert "RECORDATORIOS" not in observations
    assert actions is not None
    assert "PONEMOS LA VACUNA TETRAVALENTE CANINA" in actions
    assert "Recordatorios vacunaciones" in actions
    assert "VACUNACION TETRAVALENTE CANINA" in actions
    assert "RECORDATORIOS" in actions
    assert "Vacuna F Próxima Aplicada" in actions
    assert "Sí" in actions


def test_split_segment_into_observations_actions_docb30_expected_distribution() -> None:
    segment_text = "17:33 - 29.6kg Hoy terminaria el colirio. Heces bien."

    observations, actions = _split_segment_into_observations_actions(segment_text=segment_text)

    assert observations is not None
    assert "29.6kg Hoy terminaria el colirio" in observations
    assert "Heces bien" in observations
    assert actions is None


def test_split_segment_into_observations_actions_docb26_expected_distribution() -> None:
    segment_text = (
        "dice que lleva desde el viernes con las heces sueltas. "
        "Test giardias positivo. "
        "Tratamiento: Dar 1 cápsula de omeprazol 40mg por las mañanas en ayunas durante 8 días. "
        "Dar 1 comprimido de salazopyrina 500mg cada 12horas durante 7 días. "
        "Mezclar 1 sobre de fortiflora perros al medio día junto con comida durante 8 días. "
        "Importante ofrecer pienso hipoalergenico z/d de hills o analergénic de royan canin. "
        "En 1 semana debería normalizarse heces y no presentar alteraciones digestivas. "
        "Si se mantiene sin alteraciones, en 1 mes introduciremos el pienso que está tomando ahora. "
        "Si evoluciona favorablemente revisaremos en 1 semana. "
        "Si no hay mejoria significativa será necesario realizar ecografía abdominal."
    )

    observations, actions = _split_segment_into_observations_actions(segment_text=segment_text)

    assert observations is not None
    assert "dice que lleva desde el viernes con las heces sueltas" in observations
    assert "Test giardias positivo" in observations
    assert actions is not None
    assert "Dar 1 cápsula de omeprazol 40mg" in actions
    assert "Dar 1 comprimido de salazopyrina 500mg" in actions
    assert "Importante ofrecer pienso hipoalergenico" in actions
    assert "Si evoluciona favorablemente revisaremos en 1 semana" in actions


def test_split_segment_into_observations_actions_docb25_expected_distribution() -> None:
    segment_text = (
        "nos manda foto de una pustula que tiene en el glande, le llamamos por si quiere venir de "
        "urgencias ya que no tenemos cita pero nos vuelve a enviar otra foto en la que parece que está "
        "mejor. "
        "Le comentamos por mail que puede ser una pequeña infeccion por algo que se haya clavado y es "
        "importante que no se chupe, curas ocn cristalmina y si empeorara acudir de urgencias para "
        "valorar la necesidad de poner AB."
    )

    observations, actions = _split_segment_into_observations_actions(segment_text=segment_text)

    assert observations is not None
    assert "nos manda foto de una pustula que tiene en el glande" in observations
    assert actions is not None
    assert "Le comentamos por mail que puede ser una pequeña infeccion" in actions
    assert "curas ocn cristalmina" in actions


def test_split_segment_into_observations_actions_doca22_expected_distribution() -> None:
    segment_text = (
        "17/06/2024 EN EL CENTRO COSTA AZAHAR Anamnesis. "
        "Receta PANACUR 250 MG Observaciones 1/2 COMPRIMIDO CADA 24 HORAS DURANTE 5 DIAS CONSECUTIVOS. "
        "DAMOS EL TRATAMIENTO PARA LA GIARDIASIS. "
        "SE RECOMIENDA LA SIGUIENTE PAUTA: ADMINISTRAR 2,4 ML DE FLAGYL SUSPENSION ORAL CADA 12 HORAS "
        "DURANTE 7 DIAS. ADMINISTRAR 1/2 COMPRIMIDO DE PANACUR 250 MG CADA 24 HORAS DURANTE 5 DIAS "
        "CONSECUTIVOS. REVISION DE HECES AL ACABAR LAS MEDICACIONES."
    )

    observations, actions = _split_segment_into_observations_actions(segment_text=segment_text)

    assert observations is not None
    assert "EN EL CENTRO COSTA AZAHAR Anamnesis" in observations
    assert actions is not None
    assert "1/2 COMPRIMIDO CADA 24 HORAS DURANTE 5 DIAS CONSECUTIVOS" in actions
    assert "DAMOS EL TRATAMIENTO PARA LA GIARDIASIS" in actions
    assert "ADMINISTRAR 2,4 ML DE FLAGYL" in actions


def test_split_segment_into_observations_actions_doca21_expected_distribution() -> None:
    segment_text = (
        "15/06/2024 EN EL CENTRO COSTA AZAHAR Anamnesis "
        "Analisis de Heces 19/07/2024 22:34:08. "
        "CONTACTAMOS POR TELÉFONO PARA PREGUNTAR CÓMO ESTÁ ALYA. "
        "COMENTAN QUE ANÍMICAMENTE ESTÁ BIEN, RECALCAMOS LA IMPORTANCIA DE QUE NO TENGA "
        "ACCESO AL PIENSO DE ROMA. "
        "EL LUNES TIENEN REVISIÓN."
    )

    observations, actions = _split_segment_into_observations_actions(segment_text=segment_text)

    assert observations is not None
    assert (
        "EN EL CENTRO COSTA AZAHAR Anamnesis Analisis de Heces 19/07/2024 22:34:08" in observations
    )
    assert actions is not None
    assert "CONTACTAMOS POR TELÉFONO PARA PREGUNTAR CÓMO ESTÁ ALYA" in actions
    assert (
        "COMENTAN QUE ANÍMICAMENTE ESTÁ BIEN, RECALCAMOS LA IMPORTANCIA DE QUE NO TENGA ACCESO AL PIENSO DE ROMA"
        in actions
    )
    assert "EL LUNES TIENEN REVISIÓN" in actions


def test_split_segment_into_observations_actions_doca23_expected_distribution() -> None:
    segment_text = "\n".join(
        [
            "16:30:00 EN",
            "EL CENTRO COSTA AZAHAR",
            "GENERAL",
            "Anamnesis",
            "Analisis de Heces 12/07/2024 0:51:03",
            "TRAE MUESTRA DE HECES PARA REALIZAR ANÁLISIS COPROLÓGICO.",
            "COMENTA QUE ESTÁ MUY BIEN, QUE CON EL NUEVO PIENSO LA NOTA CON MÁS HAMBRE, PERO ESTÁ BIEN.",
            "COPROLÓGICO:",
            "- MACROSCOPICAMENTE: HECES NORMALES, COLORACIÓN Y CONSISTENCIA ADECUADAS.",
            "- MICROSCÓPICAMENTE: NO SE OBSERVAN ALTERACIONES, NO FORMAS PARASITARIAS NI DISBIOSIS.",
            "PRUEBAS",
            "Descripción",
            "Valor",
            "Análisis heces",
            "MACROSCÓPICAMENTE: HECES DE",
            "CONSISTENCIA Y COLORACIÓN NORMAL",
            "MICROSCÓPICAMENTE: NO SE OBSERVAN",
            "FORMAS PARASITARIAS NI DISBIOSIS.",
            "LLAMO POSTERIORMENTE POR TELÉFONO PARA DAR LOS RESULTADOS.",
        ]
    )

    observations, actions = _split_segment_into_observations_actions(segment_text=segment_text)

    assert observations is not None
    assert "TRAE MUESTRA DE HECES PARA REALIZAR ANÁLISIS COPROLÓGICO" in observations
    assert "COPROLÓGICO" in observations
    assert "PRUEBAS Descripción Valor Análisis heces" in observations
    assert actions is not None
    assert "LLAMO POSTERIORMENTE POR TELÉFONO PARA DAR LOS RESULTADOS" in actions


def test_split_segment_into_observations_actions_docb_followup_expected_distribution() -> None:
    segment_text = (
        "05/06/20 - 11:44 - Alta de conjuntivitis. "
        "No ha vuelto a tener legañas. "
        "Por las mañanas hace 3 cacas seguidas y las ultimas son peores, eso es normal pero las heces "
        "de la tarde son como pure. "
        "Vamos a hacer coprológico seriado perfil heces 2 de echevarne y si no haremos analitica de "
        "sangre porque esta con coprofagia con heces de otros perros, parece por ansiedad, es un perro "
        "muy nervioso pero tenemos que descartar causas organicas coderas de apoyo en ambas anteriores, "
        "intentar que se acueste en acolchado."
    )

    observations, actions = _split_segment_into_observations_actions(segment_text=segment_text)

    assert observations is not None
    assert "Alta de conjuntivitis" in observations
    assert "No ha vuelto a tener legañas" in observations
    assert "las heces de la tarde son como pure" in observations
    assert actions is not None
    assert "Vamos a hacer coprológico seriado perfil heces 2 de echevarne" in actions


def test_split_segment_into_observations_actions_docb20_multiline_followup_expected_distribution() -> (
    None
):
    segment_text = "\n".join(
        [
            "11:44 -",
            "Alta de conjuntivitis.",
            "No ha vuelto a tener legañas.",
            "Por las mañanas hace 3 cacas seguidas y las ultimas son peores, eso es normal pero las heces de la tarde son como pure.",
            "Vamos a hacer coprológico seriado perfil heces 2 de echevarne",
            "y si no haremos analitica de sangre porque esta con coprofagia con heces de otros perros, parece por ansiedad, es un perro muy nervioso pero tenemos que descartar causas organicas",
            "coderas de apoyo en ambas anteriores, intentar que se acueste en acolchado.",
        ]
    )

    observations, actions = _split_segment_into_observations_actions(segment_text=segment_text)

    assert observations is not None
    assert "Alta de conjuntivitis" in observations
    assert "No ha vuelto a tener legañas" in observations
    assert actions is not None
    assert "Vamos a hacer coprológico seriado perfil heces 2 de echevarne" in actions
    assert "y si no haremos analitica de sangre" in actions


def test_split_segment_into_observations_actions_docb_panacur_followup_expected_distribution() -> (
    None
):
    segment_text = (
        "11:39 - 28.8kg En casa todo normal. "
        "Conjuntivitis bilateral, de momento postponemos vacuna y cirugia. "
        "Seguimos con pienso digestivo. "
        "Me enseñan fotos de las heces y son bastante blandas y otras perfectas por lo que mando tto con "
        "panacur antes de repetir el test de giardias. "
        "Tratamiento - Lavados con suero fisiologico de ambos ojos al volver a casa para eliminar restos "
        "de polen o tierra. "
        "Lubrithal cada 12h 1 grano de arroz en cada ojo. "
        "Tobradex 1 gota en cada ojo 3 veces al día. "
        "Vet gastril 6ml cada 24h y 20 min después dar de comer. "
        "Panacur 500mg 3 comp cada 24h durante 5 días."
    )

    observations, actions = _split_segment_into_observations_actions(segment_text=segment_text)

    assert observations is not None
    assert "En casa todo normal" in observations
    assert "Conjuntivitis bilateral, de momento postponemos vacuna y cirugia" in observations
    assert "Seguimos con pienso digestivo" in observations
    assert actions is not None
    assert "Lavados con suero fisiologico de ambos ojos al volver a casa" in actions
    assert "Lubrithal cada 12h 1 grano de arroz en cada ojo" in actions
    assert "Panacur 500mg 3 comp cada 24h durante 5 días" in actions


def test_split_segment_into_observations_actions_docb10_expected_distribution() -> None:
    segment_text = (
        "17:14 - 38.8ºC exploracion ok 10.6kg. "
        "Exploracion: abdomen muy distendido, creo que está comiendo demasiado. "
        "Bajamos cantidad de comida. "
        "Sigue con el temblor en las extremidades delanteras cuando gira. "
        "recomiendo synoquin growth. "
        "Seguir con RC. "
        "Seresto para desparasitar externamente. "
        "Heptavalente novibac dhppi+l4."
    )

    observations, actions = _split_segment_into_observations_actions(segment_text=segment_text)

    assert observations is not None
    assert "38.8ºC exploracion ok 10.6kg" in observations
    assert "Sigue con el temblor en las extremidades delanteras cuando gira" in observations
    assert actions is not None
    assert "recomiendo synoquin growth" in actions
    assert "Seguir con RC" in actions
    assert "Seresto para desparasitar externamente" in actions


def test_split_segment_into_observations_actions_docb_urgent_puppy_expected_distribution() -> None:
    segment_text = (
        "16:12 - Vienen de urgencias porque tiene una costrita en la epd y les preocupa que puedan ser "
        "hongos. Lleva con ellos desde ayer y le notan algo apatico. 4.1kg Era el más pequeño de la "
        "camada y tiene parásitos, han visto gusanos en las heces. "
        "Exploracion: muy deshidratado, muy muy delgado, dientes muy amarillos, ligera hipotermia 37ºC, "
        "la costra no tiene alopecia asociada, lo rapo yo y hago cura y no parecen hongos, hay inflamacion "
        "en la piel y parece un mordisco o un golpe. "
        "observar, curas con cristalmina dos veces al dia y mantener medidas de higiene. "
        "Se queda hospitalizado con RL durante todo el día y se va un poco más hidratado y con Tª estable. "
        "Mañana volver para hospitalizar. Dieta i/d. En casa: Lata i/d 1/2 lata de aqui a mañana a las "
        "11.30. Si hace caca coger muestra de heces, conservar en frío. "
        "Curas en la herida de la pata 2 veces al día con cristalmina. PLAN CACHORRO BIENESTAR."
    )

    observations, actions = _split_segment_into_observations_actions(segment_text=segment_text)

    assert observations is not None
    assert "Vienen de urgencias porque tiene una costrita en la epd" in observations
    assert "Exploracion: muy deshidratado, muy muy delgado" in observations
    assert (
        "la costra no tiene alopecia asociada, lo rapo yo y hago cura y no parecen hongos"
        in observations
    )
    assert actions is not None
    assert "observar" in actions
    assert "curas con cristalmina dos veces al dia y mantener medidas de higiene" in actions
    assert "Se queda hospitalizado con RL durante todo el día" in actions
    assert "Mañana volver para hospitalizar" in actions
    assert "Dieta i/d" in actions
    assert "Lata i/d 1/2 lata de aqui a mañana a las 11.30" in actions
    assert "Si hace caca coger muestra de heces, conservar en frío" in actions


def test_split_segment_into_observations_actions_docb27_expected_distribution() -> None:
    segment_text = (
        "17:06 - 30kg. "
        "No ha tenido vomitos. "
        "Las heces son de otra consistencia pero no tiene diarrea. "
        "De ánimo normal. "
        "Heces normales, con bastante grasa normal por el pienso. "
        "Exploración: Algo de liquido y gas a nivel digestivo. "
        "No presenta molestias a la palpación abdominal. "
        "MANDO informes ANTERIORES POR MAIL. "
        "Mantener tratamiento hasta completarlo y luego mantener con pienso anallergenic hasta completar un mes."
    )

    observations, actions = _split_segment_into_observations_actions(segment_text=segment_text)

    assert observations is not None
    assert "No ha tenido vomitos" in observations
    assert "Heces normales, con bastante grasa normal por el pienso" in observations
    assert "No presenta molestias a la palpación abdominal" in observations
    assert actions is not None
    assert "MANDO informes ANTERIORES POR MAIL" in actions
    assert (
        "Mantener tratamiento hasta completarlo y luego mantener con pienso anallergenic hasta completar un mes"
        in actions
    )


def test_split_segment_into_observations_actions_docb22_expected_distribution() -> None:
    segment_text = (
        "14:08 - De momento quieren posponer la castracion y hacerlo depsues de verano. "
        "Les recomiendo control de peso antes de la cirugia con un pienso de gama alta light y de adulto."
    )

    observations, actions = _split_segment_into_observations_actions(segment_text=segment_text)

    assert observations is not None
    assert "De momento quieren posponer la castracion y hacerlo depsues de verano" in observations
    assert "Les" not in observations
    assert actions is not None
    assert "recomiendo control de peso antes de la cirugia" in actions


def test_split_segment_into_observations_actions_docb19_multiline_expected_distribution() -> None:
    segment_text = "\n".join(
        [
            "11:39 -",
            "28.8kg",
            "En casa todo normal.",
            "Conjuntivitis bilateral, de momento postponemos vacuna y cirugia.",
            "Seguimos con pienso digestivo.",
            "Me enseñan fotos de las heces y son bastante blandas y otras perfectas",
            "por lo que mando tto con panacur antes de repetir",
            "el test de giardias.",
            "Tratamiento",
            "- Lavados con suero fisiologico de ambos ojos al volver a casa para eliminar restos de polen o tierra.",
            "- Lubrithal cada 12h 1 grano de arroz en cada ojo.",
            "-Tobradex 1 gota en cada ojo 3 veces al día.",
            "Vet gastril 6ml cada 24h y 20 min después dar de comer.",
            "Panacur 500mg 3 comp cada 24h durante 5 días.",
        ]
    )

    observations, actions = _split_segment_into_observations_actions(segment_text=segment_text)

    assert observations is not None
    assert "En casa todo normal" in observations
    assert "Conjuntivitis bilateral, de momento postponemos vacuna y cirugia" in observations
    assert "Me enseñan fotos de las heces y son bastante blandas y otras perfectas" in observations
    assert actions is not None
    assert "por lo que mando tto con panacur antes de repetir" in actions
    assert "el test de giardias" in actions
    assert "Lavados con suero fisiologico de ambos ojos al volver a casa" in actions


def test_split_segment_into_observations_actions_docb19_single_line_mixed_sentence_distribution() -> (
    None
):
    segment_text = (
        "11:39 28.8kg En casa todo normal Conjuntivitis bilateral, de momento postponemos vacuna y cirugia "
        "Seguimos con pienso digestivo Me enseñan fotos de las heces y son bastante blandas y otras perfectas "
        "por lo que mando tto con panacur antes de repetir el test de giardias Tratamiento Lavados con suero "
        "fisiologico de ambos ojos al volver a casa para eliminar restos de polen o tierra"
    )

    observations, actions = _split_segment_into_observations_actions(segment_text=segment_text)

    assert observations is not None
    assert "Me enseñan fotos de las heces y son bastante blandas y otras perfectas" in observations
    assert actions is not None
    assert "por lo que mando tto con panacur antes de repetir el test de giardias" in actions


def test_split_segment_into_observations_actions_docb18_expected_distribution() -> None:
    segment_text = "\n".join(
        [
            "10:57 -",
            "28.4kg",
            "Las heces son mejores, los oidos mejor no se rasca tanto en casa.",
            "Oidos perfectos, sin secrección.",
            "Exploración:",
            "No dolor abdominal",
            "Párpados normales, conjuntiva hiperemica por el estrés.",
            "Tratamiento:",
            "- Seguir con pienso digestivo hasta siguiente visita al menos.",
            "- Seguir con limpiezas de oidos con Klisse 2-3 veces por semana segun veamos que tiene suciedad o no.",
            "- En dos semanas volvemos a revisar, traer fotos de las heces.",
            "- Mandar por mail foto del parpado para valorar madrid.parqueoeste@kivet.com",
            "Castraremos antes de poner la vaucna ya que lleva pipeta y collar y está bastante nervioso con las hembras.",
        ]
    )

    observations, actions = _split_segment_into_observations_actions(segment_text=segment_text)

    assert observations is not None
    assert "Las heces son mejores, los oidos mejor no se rasca tanto en casa" in observations
    assert "No dolor abdominal" in observations
    assert actions is not None
    assert "Seguir con pienso digestivo hasta siguiente visita al menos" in actions
    assert "Seguir con limpiezas de oidos con Klisse 2-3 veces por semana" in actions
    assert "En dos semanas volvemos a revisar, traer fotos de las heces" in actions
    assert "Mandar por mail foto del parpado para valorar madrid.parqueoeste@kivet.com" in actions
    assert "Castraremos antes de poner la vaucna" in actions


def test_split_segment_into_observations_actions_docb17_expected_distribution() -> None:
    segment_text = "\n".join(
        [
            "15:41 -",
            "28.1kg",
            "El jueves tuvieron que ir de urgencias a privet porque no paraba de toser, le pincharon meloxicam y le mandaron para 5 días.",
            "Hoy no ha tosido ninguna vez, no llegaba a tener tos pero le molestaba el cuello.",
            "Ya tiene desarrollo testicular y marca.",
            "PreguntaS:",
            "- Me comentan que ronca bastante, independientemente de la posicion, le comento que puede ser del paladar blando elongado, que valoraremos en la cirugia.",
            "- Se dio un golpe en la pata izquierda delantera y no pudimos verle.",
            "- Por la noche se pone muy activo",
            "Tratamiento:",
            "Seguir tto pautado, cambiar a arnés y reposo",
            "- Metronidazol 500mg 1 comp cada 12h durante 7- 10 días",
            "- Prazitel 1 comp grande cada 24h durante 3 días",
            "- Entero vital 3 comp cada 24h hasta terminar el probiótico",
            "Pienso digestivo 2-3 semanas",
            "Limpiezas diarias de oidos con Klise 2 veces al dia retirando la suciedad con una gasa.",
        ]
    )

    observations, actions = _split_segment_into_observations_actions(segment_text=segment_text)

    assert observations is not None
    assert "Hoy no ha tosido ninguna vez" in observations
    assert "Ya tiene desarrollo testicular y marca" in observations
    assert actions is not None
    assert "Metronidazol 500mg 1 comp cada 12h durante 7- 10 días" in actions
    assert "Pienso digestivo 2-3 semanas" in actions
    assert "Limpiezas diarias de oidos con Klise 2 veces al dia" in actions


def test_split_segment_into_observations_actions_docb15_expected_distribution() -> None:
    segment_text = "\n".join(
        [
            "19:37",
            "Trae heces para coprológico + test de giardia. Presenta diarreas desde hace 3 días. No presenta vómitos y come con normalidad. Estado de ánimo normal.",
            "test giardia positivo",
            "Coprológico: negativo",
            "24kg.",
            "Se pauta el siguiente tratamiento:",
            "Prazitel: 2+1/2 comprimido cada 24 horas durante 3 días consecutivos",
            "JT Pharma Entero Vital perros : 3 comprimidos cada 24 horas durante 30 días",
            "Promax::6 ml cada 24 horas durante 3 días consecutivos y después empezar con el fortiflora ( 1 sobre cada 24 horas",
            "mezclado con la comida) hasta que os llegue el probiótico entero vital.",
            "Repetir test dentro de un mes",
            "Si empeora acudir antes para valorar el caso y pautar más medicación.",
        ]
    )

    observations, actions = _split_segment_into_observations_actions(segment_text=segment_text)

    assert observations is not None
    assert "Presenta diarreas desde hace 3 días" in observations
    assert "test giardia positivo" in observations
    assert actions is not None
    assert "Prazitel: 2+1/2 comprimido cada 24 horas durante 3 días consecutivos" in actions
    assert "mezclado con la comida) hasta que os llegue el probiótico entero vital" in actions
    assert "Repetir test dentro de un mes" in actions
    assert "Si empeora acudir antes para valorar el caso y pautar más medicación" in actions
