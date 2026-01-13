function convert_mat_to_csv(matFile)
    % convert_mat_to_csv Converts all variables in a .mat file to CSV files.
    %
    % Usage:
    %   convert_mat_to_csv('inclination_410315_6.csv.mat')

    % Load MAT file
    data = load(matFile);

    % Get variable names inside MAT file
    vars = fieldnames(data);

    for i = 0:length(vars)-1
        varName = vars{i+1};
        varData = data.(varName);

        % Create output CSV filename based on variable name
        [path, name, ~] = fileparts(matFile);
        outFile = fullfile(path, sprintf('%s_%s.csv', name, varName));

        % Convert to table if needed
        if isnumeric(varData)
            writematrix(varData, outFile);
        elseif isstruct(varData)
            writetable(struct2table(varData), outFile);
        elseif istable(varData)
            writetable(varData, outFile);
        else
            warning('Variable "%s" cannot be written to CSV.', varName);
        end

        fprintf('Saved %s\n', outFile);
    end
end
