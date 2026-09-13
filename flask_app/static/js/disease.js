document.addEventListener(
    "DOMContentLoaded",
    function () {

        // =================================================
        // ELEMENTS
        // =================================================

        const imageInput =
            document.getElementById("imageInput");

        const preview =
            document.getElementById("preview");

        const detectBtn =
            document.getElementById("detectBtn");

        const resultCard =
            document.getElementById("resultCard");

        const cropResult =
            document.getElementById("cropResult");

        const diseaseResult =
            document.getElementById("diseaseResult");

        const confidenceResult =
            document.getElementById("confidenceResult");

        const messageResult =
            document.getElementById("messageResult");

        const causeResult =
            document.getElementById("causeResult");

        const symptomsResult =
            document.getElementById("symptomsResult");

        const treatmentResult =
            document.getElementById("treatmentResult");

        const preventionResult =
            document.getElementById("preventionResult");

        const topPredictions =
            document.getElementById("topPredictions");


        // =================================================
        // IMAGE SELECT
        // =================================================

        imageInput.addEventListener(
            "change",
            function () {

                const file =
                    imageInput.files[0];


                if (!file) {

                    preview.style.display =
                        "none";

                    detectBtn.disabled =
                        true;

                    return;
                }


                // Check image

                if (!file.type.startsWith("image/")) {

                    alert(
                        "Please select a valid image."
                    );

                    imageInput.value = "";

                    preview.style.display =
                        "none";

                    detectBtn.disabled =
                        true;

                    return;
                }


                // Preview

                const reader =
                    new FileReader();


                reader.onload =
                    function (event) {

                        preview.src =
                            event.target.result;

                        preview.style.display =
                            "block";
                    };


                reader.readAsDataURL(file);


                detectBtn.disabled =
                    false;


                // Hide old result

                resultCard.style.display =
                    "none";
            }
        );


        // =================================================
        // DETECT BUTTON
        // =================================================

        detectBtn.addEventListener(
            "click",
            async function () {

                const file =
                    imageInput.files[0];


                if (!file) {

                    alert(
                        "Please select a leaf image first."
                    );

                    return;
                }


                // Loading

                detectBtn.disabled =
                    true;

                detectBtn.innerHTML =
                    "🔄 Detecting...";


                // FormData

                const formData =
                    new FormData();

                formData.append(
                    "image",
                    file
                );


                try {

                    // -------------------------------------
                    // API REQUEST
                    // -------------------------------------

                    const response =
                        await fetch(
                            "/api/disease/predict",
                            {
                                method: "POST",
                                body: formData
                            }
                        );


                    // -------------------------------------
                    // READ RESPONSE
                    // -------------------------------------

                    const data =
                        await response.json();


                    // -------------------------------------
                    // ERROR
                    // -------------------------------------

                    if (
                        !response.ok ||
                        !data.success
                    ) {

                        throw new Error(
                            data.error ||
                            "Disease detection failed."
                        );
                    }


                    // -------------------------------------
                    // BASIC RESULT
                    // -------------------------------------

                    cropResult.textContent =
                        data.crop ||
                        "Unknown";


                    diseaseResult.textContent =
                        data.disease ||
                        "Unknown";


                    if (
                        data.confidence !==
                        undefined
                    ) {

                        confidenceResult.textContent =
                            data.confidence + "%";

                    } else {

                        confidenceResult.textContent =
                            "N/A";
                    }


                    messageResult.textContent =
                        data.message ||
                        "";


                    // -------------------------------------
                    // CAUSE
                    // -------------------------------------

                    causeResult.textContent =
                        data.cause ||
                        "Information not available.";


                    // -------------------------------------
                    // SYMPTOMS
                    // -------------------------------------

                    symptomsResult.textContent =
                        data.symptoms ||
                        "Information not available.";


                    // -------------------------------------
                    // TREATMENT
                    // -------------------------------------

                    treatmentResult.innerHTML =
                        "";


                    if (
                        Array.isArray(
                            data.treatment
                        ) &&
                        data.treatment.length > 0
                    ) {

                        data.treatment.forEach(
                            function (item) {

                                const li =
                                    document.createElement(
                                        "li"
                                    );

                                li.textContent =
                                    item;

                                treatmentResult.appendChild(
                                    li
                                );
                            }
                        );

                    } else {

                        const li =
                            document.createElement(
                                "li"
                            );

                        li.textContent =
                            "No specific treatment information available.";

                        treatmentResult.appendChild(
                            li
                        );
                    }


                    // -------------------------------------
                    // PREVENTION
                    // -------------------------------------

                    preventionResult.innerHTML =
                        "";


                    if (
                        Array.isArray(
                            data.prevention
                        ) &&
                        data.prevention.length > 0
                    ) {

                        data.prevention.forEach(
                            function (item) {

                                const li =
                                    document.createElement(
                                        "li"
                                    );

                                li.textContent =
                                    item;

                                preventionResult.appendChild(
                                    li
                                );
                            }
                        );

                    } else {

                        const li =
                            document.createElement(
                                "li"
                            );

                        li.textContent =
                            "No specific prevention information available.";

                        preventionResult.appendChild(
                            li
                        );
                    }


                    // -------------------------------------
                    // TOP 3
                    // -------------------------------------

                    topPredictions.innerHTML =
                        "";


                    if (
                        Array.isArray(
                            data.top_predictions
                        )
                    ) {

                        data.top_predictions.forEach(
                            function (item, index) {

                                const li =
                                    document.createElement(
                                        "li"
                                    );

                                li.textContent =
                                    `${index + 1}. ${item.crop} - ${item.disease} (${item.confidence}%)`;

                                topPredictions.appendChild(
                                    li
                                );
                            }
                        );
                    }


                    // -------------------------------------
                    // SHOW RESULT
                    // -------------------------------------

                    resultCard.style.display =
                        "block";


                    resultCard.scrollIntoView({
                        behavior: "smooth",
                        block: "start"
                    });


                } catch (error) {

                    console.error(
                        "Disease detection error:",
                        error
                    );

                    alert(
                        error.message ||
                        "Something went wrong."
                    );

                } finally {

                    // Restore button

                    detectBtn.disabled =
                        false;

                    detectBtn.innerHTML =
                        "🔍 Detect Disease";
                }

            }
        );

    }
);