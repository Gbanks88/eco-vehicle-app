const ForgeSDK = require('forge-apis');
const fs = require('fs').promises;
const path = require('path');

class AutodeskService {
    constructor() {
        this.clientId = process.env.AUTODESK_CLIENT_ID;
        this.clientSecret = process.env.AUTODESK_CLIENT_SECRET;
        this.bucketKey = process.env.FORGE_BUCKET_KEY;
        
        // Initialize the SDK
        this.oAuth2TwoLegged = new ForgeSDK.AuthClientTwoLegged(
            this.clientId,
            this.clientSecret,
            ['data:read', 'data:write', 'bucket:read', 'bucket:create'],
            true
        );
    }

    async authenticate() {
        try {
            const credentials = await this.oAuth2TwoLegged.authenticate();
            return credentials;
        } catch (error) {
            console.error('Authentication error:', error);
            throw error;
        }
    }

    async createBucket() {
        try {
            const credentials = await this.authenticate();
            const bucketApi = new ForgeSDK.BucketsApi();
            
            const createBucketResponse = await bucketApi.createBucket(
                {
                    bucketKey: this.bucketKey,
                    policyKey: 'persistent'
                },
                {},
                credentials
            );
            
            return createBucketResponse;
        } catch (error) {
            if (error.statusCode === 409) {
                console.log('Bucket already exists');
                return { bucketKey: this.bucketKey };
            }
            throw error;
        }
    }

    async uploadModel(filePath) {
        try {
            const credentials = await this.authenticate();
            const objectsApi = new ForgeSDK.ObjectsApi();
            
            // Read file
            const fileBuffer = await fs.readFile(filePath);
            const fileName = path.basename(filePath);
            
            // Upload to Forge
            const uploadResponse = await objectsApi.uploadObject(
                this.bucketKey,
                fileName,
                fileBuffer.length,
                fileBuffer,
                {},
                credentials
            );
            
            return uploadResponse;
        } catch (error) {
            console.error('Upload error:', error);
            throw error;
        }
    }

    async translateModel(objectName, format = 'svf') {
        const fileExtension = path.extname(objectName).toLowerCase();
        const supportedFormats = {
            '.ipt': 'inventor',    // Inventor Part
            '.iam': 'inventor',    // Inventor Assembly
            '.dwg': 'autocad',     // AutoCAD Drawing
            '.fbx': 'twinmotion',  // Twinmotion/3ds Max
            '.max': '3dsmax',      // 3ds Max
            '.rvt': 'revit',       // Revit
            '.nwd': 'navisworks',  // Navisworks
        };

        const modelFormat = supportedFormats[fileExtension] || 'generic';
        try {
            const credentials = await this.authenticate();
            const derivativesApi = new ForgeSDK.DerivativesApi();
            
            const job = {
                input: {
                    urn: Buffer.from(`urn:adsk.objects:os.object:${this.bucketKey}/${objectName}`).toString('base64')
                },
                output: {
                    formats: [
                        {
                            type: format,
                            views: ['2d', '3d'],
                            advanced: {
                                materialProperties: true,
                                textures: true,
                                lighting: true,
                                environment: true,
                                connections: modelFormat === 'inventor'
                            }
                        }
                    ]
                },
                misc: {
                    workflow: modelFormat,
                    workflowAttributes: {
                        retainPrecision: true,
                        regionalParameters: true,
                        extractConnections: modelFormat === 'inventor',
                        generateMasterViews: true,
                        extractAnalysisData: true
                    }
                }
            };
            
            const translateResponse = await derivativesApi.translate(
                job,
                { xAdsForce: true },
                credentials
            );
            
            return translateResponse;
        } catch (error) {
            console.error('Translation error:', error);
            throw error;
        }
    }

    async getViewerToken() {
        try {
            const credentials = await this.authenticate();
            return {
                access_token: credentials.access_token,
                expires_in: credentials.expires_in
            };
        } catch (error) {
            console.error('Token error:', error);
            throw error;
        }
    }
}

module.exports = new AutodeskService();
