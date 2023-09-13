// powerbi.js
var embedConfig = {
    type: 'dashboard',
    id: 'c000ba38-7f07-4277-afdf-b7afc8d9c4be',  // Replace with your report ID
    embedUrl: 'https://app.powerbi.com/reportEmbed',
    accessToken: '513486ec-6643-4f17-a508-76478311be42',  // Replace with your access token
    tokenType: models.TokenType.Embed,
    settings: {
        filterPaneEnabled: false,
        navContentPaneEnabled: true
    }
};

var reportContainer = document.getElementById('reportContainer');
var report = powerbi.embed(reportContainer, embedConfig);
