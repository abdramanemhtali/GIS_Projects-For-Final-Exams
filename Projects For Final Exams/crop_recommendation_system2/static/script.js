$(document).ready(function() {
    // Initialize
    updateModelDropdown();
    updateTiffList();

    // File input change handlers
    $('#modelFile').change(function() {
        $('#modelFileName').text(this.files[0]?.name || 'No file chosen');
    });

    $('#tiffFile').change(function() {
        $('#tiffFileName').text(this.files[0]?.name || 'No file chosen');
    });

    // Model upload
    $('#modelForm').submit(function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        const formData = new FormData(this);
        
        $('#modelStatus').html('<div class="loading"><i class="fas fa-spinner fa-spin"></i> Uploading model...</div>');
        
        $.ajax({
            url: '/upload_model',
            type: 'POST',
            data: formData,
            contentType: false,
            processData: false,
            success: function(response) {
                if (response.status === 'success') {
                    $('#modelStatus').html(`<div class="success"><i class="fas fa-check-circle"></i> ${response.message}</div>`);
                    updateModelDropdown();
                    resetForm('modelForm');
                } else {
                    $('#modelStatus').html(`<div class="error"><i class="fas fa-times-circle"></i> ${response.message}</div>`);
                }
            },
            error: function(xhr) {
                const errorMsg = xhr.responseJSON?.message || 'Server error';
                $('#modelStatus').html(`<div class="error"><i class="fas fa-times-circle"></i> Error: ${errorMsg}</div>`);
            }
        });
    });

    // TIFF upload
    $('#tiffForm').submit(function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        const formData = new FormData(this);
        
        $('#tiffStatus').html('<div class="loading"><i class="fas fa-spinner fa-spin"></i> Uploading TIFF...</div>');
        
        $.ajax({
            url: '/upload_tiff',
            type: 'POST',
            data: formData,
            contentType: false,
            processData: false,
            success: function(response) {
                if (response.status === 'success') {
                    $('#tiffStatus').html(`<div class="success"><i class="fas fa-check-circle"></i> ${response.message}</div>`);
                    updateTiffList();
                    resetForm('tiffForm');
                } else {
                    $('#tiffStatus').html(`<div class="error"><i class="fas fa-times-circle"></i> ${response.message}</div>`);
                }
            },
            error: function(xhr) {
                const errorMsg = xhr.responseJSON?.message || 'Server error';
                $('#tiffStatus').html(`<div class="error"><i class="fas fa-times-circle"></i> Error: ${errorMsg}</div>`);
            }
        });
    });

    // Prediction form
    $('#predictionForm').submit(function(e) {
        e.preventDefault();
        
        $('#predictButtonText').hide();
        $('#predictSpinner').show();
        $('#mapSection').hide();
        
        const formData = $(this).serialize();
        
        $.ajax({
            url: '/predict',
            type: 'POST',
            data: formData,
            success: function(response) {
                $('#predictButtonText').show();
                $('#predictSpinner').hide();
                
                if (response.status === 'success') {
                    $('#downloadTiffLink').attr('href', response.prediction_tiff).show();
                    $('#predictionMap').html(
                        `<iframe src="${response.map_html}" style="height:100%; width:100%; border:none;"></iframe>`
                    );
                    $('#mapSection').show();
                    $('html, body').animate({
                        scrollTop: $('#mapSection').offset().top
                    }, 500);
                } else {
                    alert(`Error: ${response.message}`);
                }
            },
            error: function(xhr) {
                $('#predictButtonText').show();
                $('#predictSpinner').hide();
                const errorMsg = xhr.responseJSON?.message || xhr.statusText;
                alert(`Error: ${errorMsg}`);
            }
        });
    });

    // Helpers
    function resetForm(formId) {
        $(`#${formId}`)[0].reset();
        if (formId === 'modelForm') {
            $('#modelFileName').text('No file chosen');
        } else if (formId === 'tiffForm') {
            $('#tiffFileName').text('No file chosen');
            $('#tiffType').val('');
        }
    }

    function updateModelDropdown() {
        $.get('/list_models', function(data) {
            if (data.status === 'success') {
                const $select = $('#selectedModel').empty().append('<option value="">-- Select a model --</option>');
                data.models.forEach(model => {
                    $select.append($('<option>', { value: model, text: model }));
                });
            }
        }).fail(function(xhr) {
            console.error('Error loading models:', xhr.responseJSON?.message || 'Server error');
        });
    }

    function updateTiffList() {
        $.get('/list_tiffs', function(data) {
            if (data.status === 'success') {
                let html = '<ul>';
                for (const [type, filename] of Object.entries(data.tiffs)) {
                    html += `<li><strong>${type}:</strong> ${filename}</li>`;
                }
                html += '</ul>';
                
                $('#uploadedTiffs').html(
                    Object.keys(data.tiffs).length ? html : '<p>No TIFF files uploaded yet</p>'
                );
            }
        }).fail(function(xhr) {
            console.error('Error loading TIFFs:', xhr.responseJSON?.message || 'Server error');
        });
    }
});